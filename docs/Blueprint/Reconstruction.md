> # ⚠️ Reconstruction payload updated — August 2026
>
> This seed is meant to **regenerate the project**, so stale figures here propagate further
> than anywhere else in the repository. The payload below has been updated to derived
> values. Sources: [REFERENCES.md](../../REFERENCES.md). Method:
> [SCIENCE_UPDATE_2026.md](../SCIENCE_UPDATE_2026.md).

```json
{
  "core": "Neural + Mycelial dual intelligence grid",
  "specs": "Reliability target unquantified; efficiency and cost-reduction claims underived",
  "scope": "MN-WI-UpMI 3 states, $39.7B-$88.5B (midpoint $64B), 5 years",
  "outcome": "165k-205k jobs sustained during build (direct+indirect+induced); 410-1,050 permanent grid O&M FTE",
  "returns": "$0.5B-$1.4B/yr congestion and dispatch savings; justify on reliability value, not energy savings",
  "proof": "Economics derived and reproducible; four core equations corrected; reliability value not yet quantified",
  "next": "Quantify reliability with LBNL ICE Calculator; decide HVAC vs HVDC; price the burial decision"
}
```

## Superseded payload

Retained so the change is auditable. **Do not regenerate from this.**

```json
{
  "core": "Neural + Mycelial dual intelligence grid",
  "specs": "99.95% reliable, 42% efficient, 35% cost reduction",
  "scope": "MN-WI-UpMI 3 states, $85B, 5 years",
  "outcome": "275k jobs, $85B annual impact, bridge to national",
  "proof": "Math validated, engineering ready, politically feasible",
  "next": "90-day political mobilization → construction launch"
}
```

### What changed and why

| Field | Problem |
|---|---|
| `$85B annual impact` | The entire MN+WI+UP electricity market is **$17.3B/yr**. An $85B annual return is roughly **5× the whole regional market**. Derived: $0.5B–$1.4B/yr. |
| `275k jobs` | Merges construction and permanent employment. Construction is defensible as 165k–205k sustained job-years; permanent grid O&M is **410–1,050 FTE**, not 150k. |
| `$85B, 5 years` | Survives as a total — the derived range is $39.7B–$88.5B — but the internal allocation was wrong by 1.9× to ~240× per line. |
| `99.95% reliable` | No supporting analysis exists. Reliability value has never been quantified for this project, which is also why the benefit-cost case is incomplete. |
| `42% efficient, 35% cost reduction` | Neither figure has a stated basis, method or baseline. |
| `Math validated` | Four core equations contained mechanical errors — a diverging φ recursion, a CAES expression mixing isothermal and adiabatic terms, a swarm product underflowing to zero, and a stray π. All corrected; see SCIENCE_UPDATE_2026.md §11. |

### On the golden ratio

φ = 1.618 remains correct for **geometric** use — spacing, radii, layout. That was never in
question.

It is **not** correct as a decay coefficient. The self-repair recursion used
`W(t+1) = φ·W(t) + ΔL·(1-φ)`, which diverges because φ > 1. The converging form uses the
reciprocal, `1/φ = φ - 1 ≈ 0.618`, and reaches the same fixed point stably. Any
reconstruction that applies "φ to everything" will reproduce that error — apply φ to
geometry, φ⁻¹ to smoothing and decay.
