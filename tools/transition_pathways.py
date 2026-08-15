#!/usr/bin/env python3
"""Transition pathways: what to change, in what order, for the least effort.

The 2026 review left the Northwoods design with open decisions rather than a
verdict. This model asks a narrower question than "is the project good?":

    Given where the design is now, which small moves buy the most, and what
    has to happen — governance and financial — before each becomes available?

Method
------
Every modification and every governance/financial step carries a cost, a lead
time, a count of parties who must consent, and a reversibility score. Those are
collapsed into a single *effort* figure in dollars, so leverage is one ratio:

    leverage = value_unlocked / effort

Effort deliberately penalises irreversibility. A free decision that forecloses a
later option is not free, and this is the whole reason grid-forming inverters
rank where they do.

Prerequisites form a DAG. The greedy pathway repeatedly takes the highest-
leverage available step, which produces both an ordering and a cumulative
value/effort curve. The *knee* of that curve is the answer to "most leveraged
small modifications" — the prefix past which further effort stops paying.

Usage
-----
    python3 tools/transition_pathways.py                # ranked moves + knee
    python3 tools/transition_pathways.py --strategies   # compare the three routes
    python3 tools/transition_pathways.py --sensitivity  # is the ranking stable?
    python3 tools/transition_pathways.py --json
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir)
TRANSITION_PATH = os.path.join(ROOT, "data", "transition_basis_2026.json")
COST_PATH = os.path.join(ROOT, "data", "cost_basis_2026.json")

BILLION = 1e9
MILLION = 1e6
KM_PER_MILE = 1.609344


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def usd(x):
    """Format a signed dollar figure at whatever scale reads cleanly."""
    a = abs(x)
    if a >= BILLION:
        return "{}${:.1f}B".format("-" if x < 0 else "", a / BILLION)
    if a >= MILLION:
        return "{}${:.0f}M".format("-" if x < 0 else "", a / MILLION)
    return "{}${:,.0f}".format("-" if x < 0 else "", a)


# ---------------------------------------------------------------------------
# Baseline: pull the derived transmission and storage figures forward so the
# modifications are scored against the corrected design, not the original one.
# ---------------------------------------------------------------------------

def baseline(cost):
    ut = cost["underground_transmission"]
    km = cost["pilot_scope"]["underground_transmission_km"]

    per_mile = ut["eei_underground_cost_usd_per_mile"]["high_range"]
    esc = ut["escalation_2017_to_2026"]["value"]
    buried_per_km = (sum(per_mile) / 2.0) / KM_PER_MILE * esc
    overhead_per_km = buried_per_km * ut["overhead_cost_ratio"]["value"]

    storage_budget = cost["pilot_scope"]["storage_budget_usd"]
    per_kwh = cost["battery_storage"]["installed_system_cost_usd_per_kwh"]["range"]
    storage_mid_per_kwh = sum(per_kwh) / 2.0

    return {
        "km": km,
        "buried_per_km": buried_per_km,
        "overhead_per_km": overhead_per_km,
        "transmission_all_buried": buried_per_km * km,
        "storage_budget": storage_budget,
        "storage_usd_per_kwh": storage_mid_per_kwh,
        # Surplus freed by the re-derivation, against the original allocation.
        "surplus_compute": 8.0 * BILLION - 34 * MILLION,
        "surplus_software": 25.0 * BILLION - 1.85 * BILLION,
        "surplus_workforce": 15.0 * BILLION - 2.3 * BILLION,
    }


# ---------------------------------------------------------------------------
# Value: what each modification is worth, computed rather than asserted.
# ---------------------------------------------------------------------------

def value_of(mod, base, cost, regional_bill):
    """Return (value_usd, explanation). Value is capex avoided or benefit unlocked."""
    mid = mod["id"]

    if mid == "M1":
        cur, prop = mod["buried_fraction_current"], mod["buried_fraction_proposed"]
        km = base["km"]
        now = cur * km * base["buried_per_km"] + (1 - cur) * km * base["overhead_per_km"]
        then = prop * km * base["buried_per_km"] + (1 - prop) * km * base["overhead_per_km"]
        return now - then, "burial {:.0%} -> {:.0%} across {:,} km".format(cur, prop, km)

    if mid == "M2":
        # Avoided risk, not a booked saving: the design has not yet committed to
        # HVDC, so this prevents an overrun rather than removing a cost.
        frac = mod["avoided_capex_risk_fraction"]
        return base["transmission_all_buried"] * frac, (
            "avoids {:.0%} converter-station overhead on a network of short segments".format(frac)
        )

    if mid == "M3":
        total = base["surplus_compute"] + base["surplus_software"] + base["surplus_workforce"]
        return total, "compute {} + software {} + workforce {} redirected".format(
            usd(base["surplus_compute"]), usd(base["surplus_software"]), usd(base["surplus_workforce"])
        )

    if mid == "M4":
        # Grid-forming does not save capex; it makes the reliability benefit
        # reachable at all. Valued as one year of the reliability term, which is
        # the conservative reading — the asset lasts decades.
        return regional_bill * 0.04, (
            "islanding and black-start capability; without it the reliability "
            "benefit term cannot be claimed"
        )

    if mid == "M5":
        km_def = mod["deferred_km"]
        avoided = km_def * base["overhead_per_km"]
        gwh = km_def * mod["storage_gwh_required_per_deferred_km"]
        storage_cost = gwh * 1e6 * base["storage_usd_per_kwh"]
        breakeven = base["overhead_per_km"] / (1e6 * base["storage_usd_per_kwh"])
        return avoided - storage_cost, (
            "defers {:,} km ({}) for {:.1f} GWh ({}) — DOES NOT PAY at the assumed "
            "{:.3f} GWh/km; breakeven is {:.4f} GWh/km ({:.0f} MWh/km)".format(
                km_def, usd(avoided), gwh, usd(storage_cost),
                mod["storage_gwh_required_per_deferred_km"], breakeven, breakeven * 1000)
        )

    if mid == "M6":
        # A contracted counterparty is worth the capital it de-risks. Valued at
        # one year of contracted revenue against the derived benefit band.
        return regional_bill * 0.08, (
            "converts speculative build into contracted revenue; changes who "
            "carries pre-construction risk"
        )

    if mid == "M7":
        return regional_bill * 0.01, "replaces an untestable expansion gate with a measurable one"

    if mid == "BUILD":
        # 15 years of the derived congestion/dispatch band, midpoint. This is the
        # only benefit the project actually books, and it books none of it until
        # financial close is reached.
        return regional_bill * 0.055 * 15, "15 yr of derived savings at 3-8% of regional spend"

    return 0.0, "no value model"


def effort_of(item, model):
    """Collapse cost, time, consent and irreversibility into one dollar figure."""
    cost = item.get("cost_usd", 0) or 0
    t = item.get("lead_time_years", 0) or 0
    parties = item.get("consenting_parties", 1) or 1
    rev = item.get("reversibility", 1.0)
    if rev is None:
        rev = 1.0

    return (
        cost * model["cost_weight"]
        + t * model["usd_per_lead_time_year"]
        + parties * model["usd_per_consenting_party"]
        + (1.0 - rev) * model["irreversibility_penalty_usd"]
    )


# ---------------------------------------------------------------------------

def build_graph(tb, base, cost, regional_bill):
    model = tb["_effort_model"]
    nodes = {}

    for mod in tb["modifications"]:
        val, why = value_of(mod, base, cost, regional_bill)
        nodes[mod["id"]] = {
            "id": mod["id"], "name": mod["name"], "kind": mod["kind"],
            "value": val, "why": why, "effort": effort_of(mod, model),
            "prereqs": mod.get("prereqs", []), "is_mod": True,
            "change": mod.get("change", ""), "rationale": mod.get("rationale", ""),
            "lead": mod.get("lead_time_years", 0), "rev": mod.get("reversibility", 1.0),
            "value_kind": mod.get("value_kind", "unspecified"),
        }

    for st in tb["steps"]:
        sval, swhy = value_of(st, base, cost, regional_bill)
        nodes[st["id"]] = {
            "id": st["id"], "name": st["name"], "kind": st["kind"],
            "value": sval, "why": swhy if sval else st.get("note", ""), "effort": effort_of(st, model),
            "prereqs": st.get("prereqs", []), "is_mod": False,
            "change": "", "rationale": st.get("note", ""),
            "lead": st.get("lead_time_years", 0), "rev": st.get("reversibility", 1.0),
            "value_kind": st.get("value_kind", "enabler"),
        }

    def flat(prereqs):
        for p in prereqs:
            if isinstance(p, list):
                for q in p:
                    yield q
            else:
                yield p

    missing = {p for n in nodes.values() for p in flat(n["prereqs"]) if p not in nodes}
    if missing:
        raise SystemExit("unknown prerequisite ids: {}".format(sorted(missing)))
    return nodes


def greedy_pathway(nodes, allowed=None):
    """Take the highest-leverage available node repeatedly.

    An enabling step has zero direct value, so it is ranked by the value it
    unblocks downstream — otherwise nothing gated would ever be chosen.
    """
    pool = set(nodes) if allowed is None else set(allowed)
    done, order = set(), []

    def unblocked_value(nid, remaining):
        """Value of this node plus everything it transitively gates."""
        total = nodes[nid]["value"]
        for other in remaining:
            deps = []
            for p in nodes[other]["prereqs"]:
                deps.extend(p if isinstance(p, list) else [p])
            if other != nid and nid in deps:
                total += nodes[other]["value"]
        return total

    while True:
        def satisfied(nid):
            for p in nodes[nid]["prereqs"]:
                if isinstance(p, list):
                    if not any(q in done for q in p):
                        return False
                elif p not in done:
                    return False
            return True

        avail = [n for n in pool - done if satisfied(n)]
        if not avail:
            break
        remaining = pool - done
        scored = []
        for n in avail:
            eff = max(nodes[n]["effort"], 1.0)
            scored.append((unblocked_value(n, remaining) / eff, nodes[n]["value"], n))
        scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
        pick = scored[0][2]
        done.add(pick)
        order.append(pick)

    stranded = sorted(pool - done)
    return order, stranded


def cumulative(order, nodes):
    rows, cv, ce, ct = [], 0.0, 0.0, 0.0
    for nid in order:
        n = nodes[nid]
        cv += n["value"]
        ce += n["effort"]
        ct = max(ct, ct + n["lead"] * 0.0) or ct  # placeholder, real time below
        rows.append({"id": nid, "cum_value": cv, "cum_effort": ce, "value": n["value"], "effort": n["effort"]})
    return rows


def critical_path_years(order, nodes):
    """Earliest finish per node given prerequisites; the max is the schedule."""
    finish = {}
    for nid in order:
        n = nodes[nid]
        ends = []
        for p in n["prereqs"]:
            if isinstance(p, list):
                got = [finish[q] for q in p if q in finish]
                ends.append(min(got) if got else 0.0)
            else:
                ends.append(finish.get(p, 0.0))
        start = max(ends or [0.0])
        finish[nid] = start + n["lead"]
    return max(finish.values()) if finish else 0.0


def find_knee(rows, fraction=0.90):
    """Smallest prefix capturing `fraction` of total positive value.

    An earlier version compared marginal leverage against the single best move.
    M3 dominates so heavily that the rule truncated after one step, which is a
    property of the metric rather than of the project.
    """
    total_positive = sum(r["value"] for r in rows if r["value"] > 0)
    if total_positive <= 0:
        return len(rows)
    acc = 0.0
    for i, r in enumerate(rows, 1):
        if r["value"] > 0:
            acc += r["value"]
        if acc >= total_positive * fraction:
            return i
    return len(rows)


# ---------------------------------------------------------------------------

def report(tb, nodes, base, regional_bill):
    out = []
    w = out.append
    line = "-" * 76

    w("=" * 76)
    w("TRANSITION PATHWAYS — most leveraged modifications, and what gates them")
    w("Basis: data/transition_basis_2026.json   Values: data/cost_basis_2026.json")
    w("=" * 76)

    w("\nBASELINE (derived, midpoints)\n" + line)
    w("  Underground transmission     {} per km".format(usd(base["buried_per_km"])))
    w("  Overhead equivalent          {} per km".format(usd(base["overhead_per_km"])))
    w("  All-buried, {:,} km          {}".format(base["km"], usd(base["transmission_all_buried"])))
    w("  Regional electricity market  {}/yr".format(usd(regional_bill)))

    mods = [n for n in nodes.values() if n["is_mod"]]
    mods.sort(key=lambda n: -(n["value"] / max(n["effort"], 1.0)))

    w("\nMODIFICATIONS RANKED BY LEVERAGE (value / effort)\n" + line)
    for n in mods:
        lev = n["value"] / max(n["effort"], 1.0)
        gate = ", ".join("(" + " or ".join(p) + ")" if isinstance(p, list) else p
                         for p in n["prereqs"]) or "none"
        w("  {}  {:>7.1f}x   {}".format(n["id"], lev, n["name"]))
        w("        value {:>8}   effort {:>8}   gated by: {}".format(
            usd(n["value"]), usd(n["effort"]), gate))
        w("        {}".format(n["why"]))
        if n["rev"] < 0.4:
            w("        ONE-WAY (reversibility {:.1f}) — cheap now, unavailable later".format(n["rev"]))
        w("")

    order, stranded = greedy_pathway(nodes)
    rows = cumulative(order, nodes)
    knee = find_knee(rows)

    w("SEQUENCE (greedy by unblocked leverage, respecting prerequisites)\n" + line)
    w("  {:<4} {:<52} {:>9} {:>9}".format("#", "step", "value", "effort"))
    for i, (nid, r) in enumerate(zip(order, rows), 1):
        n = nodes[nid]
        mark = "  <-- knee" if i == knee else ""
        tag = "" if n["is_mod"] else "  [enabler]"
        w("  {:<4} {:<52} {:>9} {:>9}{}".format(
            "{}.".format(i), (n["id"] + " " + n["name"])[:52] + tag[:0], usd(n["value"]), usd(n["effort"]), mark))
    if stranded:
        w("  stranded (prerequisites never satisfied): {}".format(", ".join(stranded)))

    # Two distinct answers, and conflating them is what makes design reviews
    # useless. "Most leveraged small modifications" means the moves available
    # right now with nobody's permission. The path to build is a different
    # question with a different timescale.
    immediate = [n for n in order
                 if nodes[n]["is_mod"] and not nodes[n]["prereqs"] and nodes[n]["value"] > 0]
    iv = sum(nodes[i]["value"] for i in immediate)
    ie = sum(nodes[i]["effort"] for i in immediate)
    pos_total = sum(nodes[i]["value"] for i in order if nodes[i]["value"] > 0)

    w("\nA. DO NOW — no prerequisites, no consent, available today\n" + line)
    w("  {} moves: {}".format(len(immediate), ", ".join(immediate)))
    w("  Value {}  for effort {}   ({:.0%} of all positive value, {:.0%} of all effort)".format(
        usd(iv), usd(ie), iv / pos_total if pos_total else 0,
        ie / sum(nodes[i]["effort"] for i in order)))
    w("  Critical path: {:.1f} years — these are decisions, not projects.".format(
        critical_path_years(immediate, nodes)))
    w("")
    for nid in immediate:
        n = nodes[nid]
        w("  {} {}  [{}]".format(n["id"], n["name"], n["value_kind"]))
        w("     -> {}".format(n["change"]))
        if n["rev"] < 0.4:
            w("     URGENT-CHEAP: reversibility {:.1f}. Free now, unavailable later.".format(n["rev"]))
        w("")

    gated = [n for n in order if nodes[n]["is_mod"] and nodes[n]["prereqs"] and nodes[n]["value"] > 0]
    w("B. GATED MODIFICATIONS — worth doing, but something must happen first\n" + line)
    for nid in gated:
        n = nodes[nid]
        w("  {} {}".format(n["id"], n["name"]))
        w("     value {}   unlocked by: {}".format(usd(n["value"]), ", ".join(
            "(" + " or ".join(p) + ")" if isinstance(p, list) else p for p in n["prereqs"])))
    w("")

    w("C. FULL PATH TO FINANCIAL CLOSE\n" + line)
    if "BUILD" in order:
        chain = order[: order.index("BUILD") + 1]
        gov = [i for i in chain if nodes[i]["kind"] in ("governance", "financial")]
        w("  {} steps, critical path {:.1f} years".format(len(chain), critical_path_years(chain, nodes)))
        w("  Governance and financial gates: {}".format(len(gov)))
        w("  Total effort to close: {}".format(usd(sum(nodes[i]["effort"] for i in chain))))
        w("  Longest pole: {}".format(
            max(chain, key=lambda i: nodes[i]["lead"]) + " ({:.1f} yr)".format(
                max(nodes[i]["lead"] for i in chain))))
        w("")
        w("  The design work is {:.0%} of the effort. The rest is permission.".format(
            sum(nodes[i]["effort"] for i in chain if nodes[i]["is_mod"])
            / sum(nodes[i]["effort"] for i in chain)))

    negatives = [n for n in order if nodes[n]["value"] < 0]
    if negatives:
        w("\nD. TESTED AND REJECTED\n" + line)
        for nid in negatives:
            n = nodes[nid]
            w("  {} {}  ({})".format(n["id"], n["name"], usd(n["value"])))
            w("     {}".format(n["why"]))

    w("\nWHAT THIS DOES NOT SAY\n" + line)
    w("  Effort weights, buried fraction, deferred km and every lead time in the")
    w("  basis file are ASSUMPTIONS, not sourced data. Run --sensitivity to see")
    w("  which conclusions survive varying them. The ordering is the output worth")
    w("  trusting; the absolute leverage numbers are not.")
    w("=" * 76)
    return "\n".join(out)


def strategies_report(tb, nodes):
    out = []
    w = out.append
    w("=" * 76)
    w("STRATEGY COMPARISON")
    w("=" * 76)
    for key, s in tb["strategies"].items():
        if key.startswith("_"):
            continue
        allowed = s["include"]
        order, stranded = greedy_pathway(nodes, allowed=allowed)
        val = sum(nodes[i]["value"] for i in order)
        eff = sum(nodes[i]["effort"] for i in order)
        yrs = critical_path_years(order, nodes)
        gates = sum(1 for i in order if nodes[i]["kind"] == "governance")
        parties = max((len(nodes[i]["prereqs"]) for i in order), default=0)
        w("\n{}\n{}".format(s["label"], "-" * 76))
        w("  value {:>9}   effort {:>9}   ratio {:>5.1f}x".format(usd(val), usd(eff), val / max(eff, 1)))
        w("  critical path {:.1f} yr   governance gates {}   deepest prereq chain {}".format(yrs, gates, parties))
        w("  order: {}".format(" -> ".join(order)))
        if stranded:
            w("  stranded: {}".format(", ".join(stranded)))
        w("  {}".format(s["note"]))
    w("\n" + "=" * 76)
    return "\n".join(out)


def sensitivity_report(tb, base, cost, regional_bill):
    """Does the ranking survive the assumptions moving? That is the real question."""
    out = []
    w = out.append
    w("=" * 76)
    w("SENSITIVITY — does the ordering hold when the assumptions move?")
    w("=" * 76)

    scenarios = [
        ("baseline", {}),
        ("time cheap (0.25x)", {"usd_per_lead_time_year": 500000}),
        ("time dear (4x)", {"usd_per_lead_time_year": 8000000}),
        ("consent cheap (0.25x)", {"usd_per_consenting_party": 375000}),
        ("consent dear (4x)", {"usd_per_consenting_party": 6000000}),
        ("irreversibility ignored", {"irreversibility_penalty_usd": 0}),
        ("irreversibility 5x", {"irreversibility_penalty_usd": 40000000}),
    ]

    rankings = {}
    for label, override in scenarios:
        tb2 = json.loads(json.dumps(tb))
        tb2["_effort_model"].update(override)
        nodes = build_graph(tb2, base, cost, regional_bill)
        mods = [n for n in nodes.values() if n["is_mod"]]
        mods.sort(key=lambda n: -(n["value"] / max(n["effort"], 1.0)))
        rankings[label] = [m["id"] for m in mods]

    ids = rankings["baseline"]
    w("\n  {:<26} {}".format("scenario", "  ".join("{:>3}".format(i) for i in ids)))
    w("  " + "-" * 72)
    for label, _ in scenarios:
        pos = {mid: rankings[label].index(mid) + 1 for mid in ids}
        w("  {:<26} {}".format(label, "  ".join("{:>3}".format(pos[i]) for i in ids)))
    w("\n  Columns are baseline order; cells are that modification's rank in each")
    w("  scenario. A column that stays flat is a robust conclusion.")

    stable = [i for i in ids if len({rankings[l].index(i) for l, _ in scenarios}) == 1]
    w("\n  Rank-stable across every scenario: {}".format(", ".join(stable) if stable else "none"))
    top3 = set(ids[:3])
    always_top3 = [i for i in ids if all(set(rankings[l][:3]) >= {i} for l, _ in scenarios)]
    w("  Always in the top 3: {}".format(", ".join(sorted(always_top3)) if always_top3 else "none"))
    w("=" * 76)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strategies", action="store_true", help="compare the three routes")
    ap.add_argument("--sensitivity", action="store_true", help="test the assumptions")
    ap.add_argument("--json", action="store_true", help="machine-readable")
    args = ap.parse_args()

    tb = load(TRANSITION_PATH)
    cost = load(COST_PATH)
    base = baseline(cost)

    d = cost["regional_market_denominators"]
    regional_bill = (
        d["minnesota_retail_sales_mwh_2024"]["value"] * d["minnesota_avg_retail_price_usd_per_mwh_2024"]["value"]
        + d["wisconsin_retail_sales_mwh_2024"]["value"] * d["wisconsin_avg_retail_price_usd_per_mwh_2024"]["value"]
        + d["michigan_up_retail_sales_mwh_estimate"]["value"] * 125.0
    )

    nodes = build_graph(tb, base, cost, regional_bill)

    if args.json:
        order, stranded = greedy_pathway(nodes)
        rows = cumulative(order, nodes)
        knee = find_knee(rows)
        json.dump({
            "order": order,
            "stranded": stranded,
            "knee_index": knee,
            "knee_set": order[:knee],
            "critical_path_years": critical_path_years(order[:knee], nodes),
            "modifications": [
                {"id": n["id"], "name": n["name"], "value_usd": n["value"],
                 "effort_usd": n["effort"], "leverage": n["value"] / max(n["effort"], 1.0)}
                for n in sorted((x for x in nodes.values() if x["is_mod"]),
                                key=lambda n: -(n["value"] / max(n["effort"], 1.0)))
            ],
        }, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    if args.strategies:
        print(strategies_report(tb, nodes))
        return
    if args.sensitivity:
        print(sensitivity_report(tb, base, cost, regional_bill))
        return

    print(report(tb, nodes, base, regional_bill))


if __name__ == "__main__":
    main()
