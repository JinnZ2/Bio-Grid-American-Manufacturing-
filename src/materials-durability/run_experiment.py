"""
run_experiment.py  --  CC0

Entry point for the structural longevity experiment.

USAGE
  python3 run_experiment.py                          # survival surface, all regimes
  python3 run_experiment.py --regime seismic --n 4000 --horizon 500
  python3 run_experiment.py --life dry_stone --regime wet_clay   # single-life trace
  python3 run_experiment.py --modes dry_stone --regime freeze_thaw  # failure-mode clocks
  python3 run_experiment.py --json
"""

import argparse
import json

from simulate import survival_surface, REGIMES, draw_env
from degradation import simulate_life
from failure_modes import failure_times, critical_mode
from archetypes import make, ARCHETYPES
from renewal import compare as renewal_compare
import random

BAR = "=" * 74


def render_surface(regime, n, horizon, seed):
    surf = survival_surface(regime, horizon=horizon, n=n, seed=seed)
    rows = sorted(surf.items(), key=lambda kv: kv[1]["survival_frac"], reverse=True)
    print(BAR)
    print(f"SURVIVAL SURFACE  regime={regime}  horizon={horizon}yr  n={n} environments")
    print(BAR)
    print(f"{'archetype':20s}{'survive%':>10}{'median_collapse':>18}{'first_mode':>22}")
    print("-" * 74)
    for a, r in rows:
        sv = r["survival_frac"] * 100
        mc = r["median_collapse"] if r["median_collapse"] is not None else "—"
        print(f"{a:20s}{sv:>9.1f}%{str(mc):>18}{r['dominant_first_mode']:>22}")
    print(BAR)


def render_all(n, horizon, seed):
    for regime in REGIMES:
        render_surface(regime, n, horizon, seed)
        print()


def render_life(archetype, regime, seed):
    rng = random.Random(seed)
    env = draw_env(rng, regime)
    res = simulate_life(archetype, env, years=1000)
    print(BAR)
    print(f"SINGLE LIFE  {archetype}  in  {regime}")
    print(BAR)
    print(f"environment: T={env.temperature_c:.0f}C hum={env.humidity_pct:.0f}% "
          f"gw={env.groundwater_level:.2f} ft_cyc={env.freeze_thaw_cycles} "
          f"salt={env.salinity:.2f} seis={env.seismic_factor:.2f} "
          f"settle={env.settlement_rate:.4f}")
    print(f"initial redundancy (load-path columns): {res['initial_redundancy']}")
    print(f"collapse year: {res['collapse_year'] if res['collapse_year'] else 'SURVIVED 1000'}")
    print("-" * 74)
    print(f"{'year':>6}{'redundancy':>12}{'capacity%':>12}")
    for y, r, cap in res["trajectory"]:
        bar = "#" * int(cap * 30)
        print(f"{y:>6}{r:>12}{cap*100:>11.0f}% {bar}")
    print(BAR)


def render_modes(archetype, regime, seed):
    rng = random.Random(seed)
    env = draw_env(rng, regime)
    s = make(archetype, env)
    times = failure_times(s)
    name, t = critical_mode(s)
    print(BAR)
    print(f"FAILURE-MODE CLOCKS  {archetype}  in  {regime}")
    print("(time-to-threshold in years; shortest = occurs first)")
    print(BAR)
    for m, yr in sorted(times.items(), key=lambda kv: kv[1]):
        flag = "  <== FIRST" if m == name else ""
        ys = f"{yr:,.1f}" if yr != float("inf") else "inf"
        print(f"  {m:24s}{ys:>14} yr{flag}")
    print(BAR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regime", default=None, choices=list(REGIMES.keys()))
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--horizon", type=int, default=500)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--life", default=None, choices=ARCHETYPES)
    ap.add_argument("--modes", default=None, choices=ARCHETYPES)
    ap.add_argument("--renewal", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.json:
        regimes = [args.regime] if args.regime else list(REGIMES.keys())
        data = {r: survival_surface(r, horizon=args.horizon, n=args.n, seed=args.seed)
                for r in regimes}
        print(json.dumps(data, indent=2))
        return

    if args.renewal:
        regime = args.regime or "temperate_stable"
        surf = survival_surface(regime, horizon=args.horizon, n=args.n, seed=args.seed)
        medians = {a: r["median_collapse"] for a, r in surf.items()}
        rows = renewal_compare(medians, horizon=args.horizon)
        print(BAR)
        print(f"RENEWAL LENS  regime={regime}  horizon={args.horizon}yr  n={args.n}")
        print(BAR)
        hdr = f"{'archetype':<22}{'intent':<11}{'fitness':>7}  {'sub_debt_flux':>14}  {'build_flux':>10}  verdict"
        print(hdr)
        print("-" * 74)
        for r in rows:
            print(f"{r['archetype']:<22}{r['intent']:<11}{r['fitness']:>7.3f}  "
                  f"{r['substrate_debt_flux']:>14.5f}  {r['build_burden_flux']:>10.5f}  {r['verdict']}")
        print(BAR)
        return

    if args.life:
        render_life(args.life, args.regime or "wet_clay", args.seed)
        return
    if args.modes:
        render_modes(args.modes, args.regime or "wet_clay", args.seed)
        return

    if args.regime:
        render_surface(args.regime, args.n, args.horizon, args.seed)
    else:
        render_all(args.n, args.horizon, args.seed)


if __name__ == "__main__":
    main()
