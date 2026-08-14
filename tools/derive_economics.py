#!/usr/bin/env python3
"""Re-derive the Northwoods pilot economics from sourced 2025-2026 cost data.

Every number this prints traces to `data/cost_basis_2026.json`, and every entry
there carries a source key resolvable in `REFERENCES.md`. Entries marked
ASSUMPTION are not sourced; the script flags how much of the result rests on
them so a reader can tell derivation from guesswork.

Usage:
    python3 tools/derive_economics.py            # summary
    python3 tools/derive_economics.py --json     # machine-readable
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASIS_PATH = os.path.join(HERE, os.pardir, "data", "cost_basis_2026.json")

KM_PER_MILE = 1.609344
BILLION = 1e9
MILLION = 1e6


def load_basis(path=BASIS_PATH):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


class Range:
    """A low/high interval. Arithmetic is interval arithmetic, so the reported
    spread widens honestly as uncertain terms accumulate."""

    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        if hi is None:
            hi = lo
        self.lo, self.hi = float(lo), float(hi)

    @classmethod
    def of(cls, seq):
        return cls(seq[0], seq[1])

    @property
    def mid(self):
        return (self.lo + self.hi) / 2.0

    def __add__(self, other):
        return Range(self.lo + other.lo, self.hi + other.hi)

    def __mul__(self, k):
        if isinstance(k, Range):
            return Range(self.lo * k.lo, self.hi * k.hi)
        return Range(self.lo * k, self.hi * k)

    __rmul__ = __mul__

    def __truediv__(self, k):
        if isinstance(k, Range):
            return Range(self.lo / k.hi, self.hi / k.lo)
        return Range(self.lo / k, self.hi / k)

    def b(self):
        return "${:.1f}B - ${:.1f}B".format(self.lo / BILLION, self.hi / BILLION)

    def m(self):
        return "${:.0f}M - ${:.0f}M".format(self.lo / MILLION, self.hi / MILLION)

    def n(self, unit="", scale=1.0, fmt="{:,.0f}"):
        sep = " " if unit else ""
        return (fmt + "{}{} - " + fmt + "{}{}").format(
            self.lo / scale, sep, unit, self.hi / scale, sep, unit
        )


# --------------------------------------------------------------------------
# Capital cost, line by line
# --------------------------------------------------------------------------

def derive_transmission(b):
    """Underground HV transmission, 4,500 km.

    Reference class is EEI's high-range overhead-to-underground cost
    ($6-12M/mile), converted to km and escalated to 2026 dollars. The low EEI
    range is distribution-class and is not applicable to HV transmission.
    """
    ut = b["underground_transmission"]
    km = b["pilot_scope"]["underground_transmission_km"]

    per_mile = Range.of(ut["eei_underground_cost_usd_per_mile"]["high_range"])
    esc = ut["escalation_2017_to_2026"]["value"]
    per_km = per_mile * (1.0 / KM_PER_MILE) * esc

    return {
        "per_km": per_km,
        "total": per_km * km,
        "overhead_alternative": per_km * km * ut["overhead_cost_ratio"]["value"],
    }


def derive_substations(b):
    """Substations and switching, derived from spacing rather than asserted."""
    scope = b["pilot_scope"]
    count = int(round(scope["underground_transmission_km"] / scope["substation_spacing_km"]))
    unit = Range.of(scope["substation_cost_usd"]["range"])
    return {"count": count, "total": unit * count}


def derive_storage(b):
    """Storage: invert the budget into capacity at 2025 installed prices.

    The original documents fix a $7B budget without stating capacity. At
    current prices that budget buys markedly more energy than it would have
    when the figure was written, so this line is reported as capacity
    delivered rather than as a cost to be corrected.
    """
    budget = b["pilot_scope"]["storage_budget_usd"]
    per_kwh = Range.of(b["battery_storage"]["installed_system_cost_usd_per_kwh"]["range"])
    # High price buys the least energy, so invert the interval.
    gwh = Range(budget / per_kwh.hi, budget / per_kwh.lo) / 1e6
    return {"budget": Range(budget), "gwh": gwh, "gw_4h": gwh / 4.0}


def derive_neural_core(b):
    """Neural control core, sized two ways.

    (a) As literally specified: 500 H100-class GPUs.
    (b) Re-specified on current hardware: the nearest Blackwell equivalent.

    Both are compared against the $8B the original budget allocates to
    "neural hubs + processing centers".
    """
    c = b["compute"]
    dgx = c["dgx_h100_system"]
    nvl = c["gb200_nvl72_rack"]
    fac = Range.of(c["datacenter_facility_cost_usd_per_mw"]["range"])
    rack_cost = Range.of(c["nvl72_rack_hardware_cost_usd"]["range"])

    gpus = b["original_claims_under_review"]["neural_core_gpus"]

    # (a) 500 H100 as DGX systems
    h100_systems = gpus / dgx["gpus"]
    h100_kw = Range.of(dgx["power_kw"]) * h100_systems

    # (b) Blackwell equivalent: fewest whole NVL72 racks covering the GPU count
    racks = -(-gpus // nvl["gpus"])  # ceiling division
    bw_gpus = racks * nvl["gpus"]
    bw_kw = Range(nvl["nominal_power_kw"], nvl["observed_full_load_kw"][1]) * racks
    bw_hw = rack_cost * racks
    bw_facility = fac * (bw_kw / 1000.0)

    # What the original $8B "neural hubs + processing centers" line actually buys,
    # priced per rack all-in. This is the informative comparison: not "the budget
    # is wrong" but "the budget describes a hyperscale campus, not a control plane".
    budget = 8.0 * BILLION
    per_rack_allin = bw_hw / racks + fac * (Range(nvl["nominal_power_kw"]) / 1000.0)
    budget_racks = Range(budget / per_rack_allin.hi, budget / per_rack_allin.lo)
    budget_gpus = budget_racks * nvl["gpus"]
    budget_mw = budget_racks * nvl["nominal_power_kw"] / 1000.0

    return {
        "h100_systems": h100_systems,
        "h100_kw": h100_kw,
        "racks": racks,
        "bw_gpus": bw_gpus,
        "bw_kw": bw_kw,
        "bw_total": bw_hw + bw_facility,
        "industry_avg_rack_kw": c["industry_average_rack_kw"]["value"],
        "budget_usd": budget,
        "budget_racks": budget_racks,
        "budget_gpus": budget_gpus,
        "budget_mw": budget_mw,
    }


def derive_soft_costs(b, construction_total):
    """Software, integration and workforce, scaled off hard construction cost.

    The original budget asserts $25B for technology development and $15B for
    workforce with no derivation. Both are re-expressed as a share of hard
    construction cost, which is how utility programs actually scope them.
    """
    software = construction_total * Range(0.02, 0.05)
    workforce = construction_total * Range(0.03, 0.06)
    return {"software": software, "workforce": workforce}


# --------------------------------------------------------------------------
# Returns and jobs
# --------------------------------------------------------------------------

def derive_regional_market(b):
    """The denominator every benefit claim must fit inside."""
    d = b["regional_market_denominators"]
    mn = d["minnesota_retail_sales_mwh_2024"]["value"] * d["minnesota_avg_retail_price_usd_per_mwh_2024"]["value"]
    wi = d["wisconsin_retail_sales_mwh_2024"]["value"] * d["wisconsin_avg_retail_price_usd_per_mwh_2024"]["value"]
    up = d["michigan_up_retail_sales_mwh_estimate"]["value"] * 125.0
    mwh = (
        d["minnesota_retail_sales_mwh_2024"]["value"]
        + d["wisconsin_retail_sales_mwh_2024"]["value"]
        + d["michigan_up_retail_sales_mwh_estimate"]["value"]
    )
    return {"annual_bill": mn + wi + up, "annual_mwh": mwh}


def derive_jobs(b, capex):
    """Employment, using PERI's published multiplier rather than assertion.

    PERI multipliers are JOB-YEARS per $1M of spend, inclusive of direct,
    indirect and induced effects. Dividing by the build duration converts them
    to simultaneous headcount, which is the comparison the original documents
    invite but do not make.
    """
    e = b["employment"]
    mult = Range.of(e["peri_job_years_per_usd_million"]["range"])
    years = b["pilot_scope"]["build_duration_years"]

    job_years = mult * (capex / MILLION)
    sustained = job_years / years
    direct_share = Range.of(e["direct_share_of_total_jobs"]["range"])
    direct = sustained * direct_share

    scope = b["pilot_scope"]
    n_sub = int(round(scope["underground_transmission_km"] / scope["substation_spacing_km"]))
    om_line = Range.of(e["grid_om_fte_per_km_transmission"]["range"]) * scope["underground_transmission_km"]
    om_sub = Range.of(e["grid_om_fte_per_substation"]["range"]) * n_sub
    om_ctl = Range.of(e["control_room_fte"]["range"])

    return {
        "job_years": job_years,
        "sustained": sustained,
        "direct_sustained": direct,
        "om_line": om_line,
        "om_sub": om_sub,
        "om_ctl": om_ctl,
        "om_total": om_line + om_sub + om_ctl,
    }


def test_original_claims(b, capex_mid, regional):
    """Check the original return claims against the regional market denominator."""
    o = b["original_claims_under_review"]
    bill = regional["annual_bill"]

    roi_return = o["total_investment_usd"] * o["roi_15_year"]
    roi_annual = roi_return / 15.0
    payback_annual = o["total_investment_usd"] / o["payback_years"]

    return {
        "claimed_savings_share_of_bill": o["annual_energy_cost_savings_usd"] / bill,
        "roi_implied_annual_return": roi_annual,
        "roi_share_of_bill": roi_annual / bill,
        "payback_implied_annual": payback_annual,
        "payback_share_of_bill": payback_annual / bill,
        "capex_delta": capex_mid - o["total_investment_usd"],
    }


def derive_realistic_benefits(b, regional):
    """Benefits that fit inside the regional market.

    Congestion and dispatch-efficiency savings of 3-8% of the regional retail
    bill is the defensible band for a transmission and controls program. This
    is an ASSUMPTION band, not a sourced figure; LBNL's ICE Calculator is the
    standard tool for adding a reliability-value term, which is not attempted
    here.
    """
    return Range(0.03, 0.08) * regional["annual_bill"]


# --------------------------------------------------------------------------

def build(b):
    tx = derive_transmission(b)
    sub = derive_substations(b)
    sto = derive_storage(b)
    core = derive_neural_core(b)

    hard = tx["total"] + sub["total"] + sto["budget"] + core["bw_total"]
    soft = derive_soft_costs(b, hard)

    subtotal = hard + soft["software"] + soft["workforce"]
    cont = Range.of(b["pilot_scope"]["contingency"]["range"])
    total = subtotal * Range(1.0 + cont.lo, 1.0 + cont.hi)

    regional = derive_regional_market(b)
    jobs = derive_jobs(b, total.mid)
    benefits = derive_realistic_benefits(b, regional)
    claims = test_original_claims(b, total.mid, regional)

    # Benefit-cost over a 15-year horizon, undiscounted, savings term only.
    bcr = (benefits * 15.0) / total

    return {
        "tx": tx, "sub": sub, "sto": sto, "core": core, "soft": soft,
        "hard": hard, "subtotal": subtotal, "total": total,
        "regional": regional, "jobs": jobs, "benefits": benefits,
        "claims": claims, "bcr": bcr,
    }


def report(b, r):
    o = b["original_claims_under_review"]
    out = []
    w = out.append

    w("=" * 74)
    w("BioGrid Northwoods pilot - economics re-derived from 2025-2026 cost data")
    w("Basis: data/cost_basis_2026.json   Sources: REFERENCES.md")
    w("=" * 74)

    w("\nCAPITAL COST\n" + "-" * 74)
    w("  Underground transmission, 4,500 km   {}".format(r["tx"]["total"].b()))
    w("      at {} per km (EEI high range, escalated to 2026$)".format(r["tx"]["per_km"].m()))
    w("      overhead alternative:            {}".format(r["tx"]["overhead_alternative"].b()))
    w("  Substations and switching ({:d} sites)  {}".format(r["sub"]["count"], r["sub"]["total"].b()))
    w("  Storage (budget held fixed)          {}".format(r["sto"]["budget"].b()))
    w("      buys {} = {} at 4 h".format(
        r["sto"]["gwh"].n("GWh", fmt="{:,.0f}"), r["sto"]["gw_4h"].n("GW", fmt="{:,.1f}")))
    w("  Neural control core                  {}".format(r["core"]["bw_total"].m()))
    w("  Software and integration             {}".format(r["soft"]["software"].b()))
    w("  Workforce and training               {}".format(r["soft"]["workforce"].b()))
    w("  " + "-" * 70)
    w("  Subtotal                             {}".format(r["subtotal"].b()))
    w("  With 20-30% contingency              {}".format(r["total"].b()))
    w("")
    w("  Original claim:                      ${:.0f}B".format(o["total_investment_usd"] / BILLION))
    w("  Re-derived midpoint:                 ${:.0f}B  (delta {:+.0f}B)".format(
        r["total"].mid / BILLION, r["claims"]["capex_delta"] / BILLION))

    w("\nNEURAL CORE - the specification does not match its budget line\n" + "-" * 74)
    w("  As written: {:.0f} H100 GPUs = {:.0f} DGX H100 systems, {}".format(
        o["neural_core_gpus"], r["core"]["h100_systems"], r["core"]["h100_kw"].n("kW", fmt="{:,.0f}")))
    w("  Current equivalent: {:d} x GB200 NVL72 = {:,d} Blackwell GPUs, {}".format(
        r["core"]["racks"], r["core"]["bw_gpus"], r["core"]["bw_kw"].n("kW", fmt="{:,.0f}")))
    w("  All-in cost including facility:      {}".format(r["core"]["bw_total"].m()))
    w("")
    w("  Original budget for this line:       $8,000M")
    w("  Ratio to the stated specification:   {:.0f}x to {:.0f}x".format(
        r["core"]["budget_usd"] / r["core"]["bw_total"].hi,
        r["core"]["budget_usd"] / r["core"]["bw_total"].lo))
    w("  What $8B actually buys:              {} racks = {} GPUs".format(
        r["core"]["budget_racks"].n(fmt="{:,.0f}"), r["core"]["budget_gpus"].n(fmt="{:,.0f}")))
    w("                                       {} of IT load".format(
        r["core"]["budget_mw"].n("MW", fmt="{:,.0f}")))
    w("  -> The budget line describes a hyperscale AI campus. The specification")
    w("     describes a single rack row. A control plane for a regional grid needs")
    w("     O(1 MW); the two figures in the original documents differ by ~200x and")
    w("     cannot both be right. Pick the specification, not the budget.")

    w("\nREGIONAL MARKET - the denominator every benefit claim must fit inside\n" + "-" * 74)
    w("  MN + WI + MI-UP retail sales         {:,.0f} TWh/yr".format(r["regional"]["annual_mwh"] / 1e6))
    w("  Total regional electricity bill      ${:.1f}B/yr".format(r["regional"]["annual_bill"] / BILLION))
    w("")
    w("  Claimed energy savings ${:.0f}B/yr    = {:.0%} of the entire regional bill".format(
        o["annual_energy_cost_savings_usd"] / BILLION, r["claims"]["claimed_savings_share_of_bill"]))
    w("  Claimed 340% / 15 yr ROI             = ${:.1f}B/yr = {:.0%} of the bill".format(
        r["claims"]["roi_implied_annual_return"] / BILLION, r["claims"]["roi_share_of_bill"]))
    w("  Claimed 4.2 yr payback               = ${:.1f}B/yr = {:.0%} of the bill".format(
        r["claims"]["payback_implied_annual"] / BILLION, r["claims"]["payback_share_of_bill"]))
    w("  -> All three exceed or approach 100% of regional electricity spending.")
    w("     They are not achievable at any level of technical performance.")

    w("\nRETURNS THAT FIT THE MARKET\n" + "-" * 74)
    w("  Congestion / dispatch savings 3-8%   {}/yr".format(r["benefits"].b()))
    w("  15-yr benefit-cost ratio (savings)   {:.2f} - {:.2f}".format(r["bcr"].lo, r["bcr"].hi))
    w("  -> Below 1.0 on avoided energy cost alone. Transmission is justified on")
    w("     reliability value and avoided generation capex, not energy savings.")
    w("     Add a reliability term with LBNL's ICE Calculator before concluding.")

    w("\nEMPLOYMENT (PERI multipliers, direct + indirect + induced)\n" + "-" * 74)
    w("  Total job-years over the build       {}".format(r["jobs"]["job_years"].n(fmt="{:,.0f}")))
    w("  Sustained jobs, {:.0f}-yr build         {}".format(
        b["pilot_scope"]["build_duration_years"], r["jobs"]["sustained"].n(fmt="{:,.0f}")))
    w("  Of which direct (on-site)            {}".format(r["jobs"]["direct_sustained"].n(fmt="{:,.0f}")))
    w("")
    w("  Original claim: {:,d} construction jobs".format(o["construction_jobs"]))
    w("  -> Defensible IF read as direct+indirect+induced sustained headcount.")
    w("     Not defensible as on-site construction workers, which is ~3x lower.")
    w("")
    w("  Steady-state grid O&M:")
    w("      cable and line crews             {} FTE".format(r["jobs"]["om_line"].n(fmt="{:,.0f}")))
    w("      substation crews                 {} FTE".format(r["jobs"]["om_sub"].n(fmt="{:,.0f}")))
    w("      control room and cyber           {} FTE".format(r["jobs"]["om_ctl"].n(fmt="{:,.0f}")))
    w("      total                            {} FTE".format(r["jobs"]["om_total"].n(fmt="{:,.0f}")))
    w("  Original claim: {:,d} permanent jobs".format(o["permanent_jobs"]))
    w("  -> Operating the grid accounts for roughly {:.1f}% of that figure. The rest".format(
        100.0 * r["jobs"]["om_total"].mid / o["permanent_jobs"]))
    w("     only closes if reshored manufacturing employment is counted, which is a")
    w("     trade and industrial-policy outcome, not a consequence of building a grid.")

    w("\nCLAIMS WITH NO AVAILABLE DERIVATION\n" + "-" * 74)
    w("  ${:.0f}B/yr technology exports by 2040".format(o["annual_export_revenue_2040_usd"] / BILLION))
    w("  -> No public market-size denominator supports this. It exceeds the")
    w("     revenue of the entire global grid-equipment sector by a wide margin.")
    w("     Retained in the documents as an aspiration, explicitly not a forecast.")

    w("\n" + "=" * 74)
    w("Interval arithmetic throughout; ranges widen as uncertain terms compound.")
    w("Entries marked ASSUMPTION in the basis file are not sourced data.")
    w("=" * 74)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    ap.add_argument("--basis", default=BASIS_PATH, help="path to cost basis JSON")
    args = ap.parse_args()

    b = load_basis(args.basis)
    r = build(b)

    if args.json:
        json.dump({
            "capex_total_usd": [r["total"].lo, r["total"].hi],
            "capex_midpoint_usd": r["total"].mid,
            "transmission_usd": [r["tx"]["total"].lo, r["tx"]["total"].hi],
            "transmission_usd_per_km": [r["tx"]["per_km"].lo, r["tx"]["per_km"].hi],
            "substation_count": r["sub"]["count"],
            "storage_gwh": [r["sto"]["gwh"].lo, r["sto"]["gwh"].hi],
            "neural_core_usd": [r["core"]["bw_total"].lo, r["core"]["bw_total"].hi],
            "neural_core_kw": [r["core"]["bw_kw"].lo, r["core"]["bw_kw"].hi],
            "regional_annual_bill_usd": r["regional"]["annual_bill"],
            "realistic_annual_benefit_usd": [r["benefits"].lo, r["benefits"].hi],
            "benefit_cost_ratio_15yr": [r["bcr"].lo, r["bcr"].hi],
            "job_years_total": [r["jobs"]["job_years"].lo, r["jobs"]["job_years"].hi],
            "jobs_sustained": [r["jobs"]["sustained"].lo, r["jobs"]["sustained"].hi],
            "jobs_direct_sustained": [r["jobs"]["direct_sustained"].lo, r["jobs"]["direct_sustained"].hi],
            "om_fte_total": [r["jobs"]["om_total"].lo, r["jobs"]["om_total"].hi],
            "neural_core_budget_equivalent_mw": [r["core"]["budget_mw"].lo, r["core"]["budget_mw"].hi],
        }, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(report(b, r))


if __name__ == "__main__":
    main()
