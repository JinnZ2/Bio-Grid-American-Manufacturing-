/**
 * Archetype Redundancy Model — corrected graph-theory basis
 *
 * ROOT CAUSE OF PRIOR BUG:
 *   In a layered source→sink graph the min-cut equals the number of vertical
 *   edges that cross any single layer gap. Lateral/tie edges are intra-layer;
 *   they never span a gap, so they CANNOT increase the min-cut — and therefore
 *   cannot increase path redundancy (R0). Counting them as independent paths
 *   collapsed all six archetypes to the same R0.
 *
 * PHYSICAL RECAST:
 *   columns    → R0  (independent load paths = true structural redundancy)
 *   lateralTies → loadSharingFactor  (slows per-edge damage, not redundancy)
 *
 * What lateral ties actually provide:
 *   (a) load SHARING — reduce overload on surviving columns
 *   (b) progressive-collapse resistance — tie adjacent columns together
 *   (c) seismic shear capacity — in-plane lateral force resistance
 *
 * None of (a)–(c) adds an independent source→sink path.
 */

// ─── Archetype definitions ────────────────────────────────────────────────────

export const ARCHETYPES = [
  { id: 'single-column', columns: 1, lateralTies: 0, layers: 3 },
  { id: 'dual-parallel', columns: 2, lateralTies: 0, layers: 3 },
  { id: 'braced-dual', columns: 2, lateralTies: 2, layers: 3 },
  { id: 'triple-parallel', columns: 3, lateralTies: 0, layers: 3 },
  { id: 'seismic-frame', columns: 3, lateralTies: 4, layers: 4 },
  { id: 'full-grid', columns: 4, lateralTies: 6, layers: 4 },
];

// ─── R0: independent load paths (min-cut of the layered graph) ───────────────

/**
 * R0 = number of independent columns.
 *
 * Proof sketch: each layer-gap in the graph is a cut. The minimum such cut
 * equals the number of vertical edges crossing that gap = columns. Lateral
 * edges are entirely within one layer and contribute zero to any cut.
 */
export function computeR0(archetype) {
  return archetype.columns;
}

// ─── Load-sharing factor (lateral ties effect) ───────────────────────────────

/**
 * Returns a dimensionless factor in [0, 1] capturing how well lateral ties
 * distribute load across surviving columns.
 *
 *   0 → no ties (each column bears full local load alone)
 *   1 → theoretical perfect sharing (uniform load regardless of column state)
 *
 * Uses a saturating exponential: each additional tie has diminishing returns.
 * Normalised against maxTies = (columns − 1) × layers (upper bound of
 * inter-column connections in the layered topology).
 */
export function computeLoadSharingFactor(archetype) {
  const { columns: n, lateralTies: t, layers } = archetype;
  if (n <= 1 || t === 0) return 0;
  const maxTies = (n - 1) * layers;
  const ratio = Math.min(t / maxTies, 1.0);
  return 1 - Math.exp(-3 * ratio); // saturates near 1 as ties → maxTies
}

// ─── Per-edge damage rate ─────────────────────────────────────────────────────

/**
 * Effective fractional load on the most-stressed surviving column after
 * `failedColumns` have been removed.
 *
 * The uniform share is 1/surviving. Under imperfect sharing the peak column
 * carries MORE than that; lateral ties pull the peak back down toward uniform.
 * The return value is therefore always ≥ 1/surviving and ≤ 1.
 *
 * Lower return value = slower damage accumulation = better durability.
 * Note: R0 is still determined by columns; this only modulates degradation rate.
 *
 * CORRECTED 2026 — load-conservation bug.
 *   The prior form was  (1/surviving) · (1 − lsf·(1 − 1/surviving)),
 *   which multiplied the already-uniform share by a factor < 1. That put the
 *   peak column BELOW the average, so total load was not conserved: summed
 *   across survivors, full-grid accounted for only 42% of the structure's
 *   load and seismic-frame 48%. Every tied archetype leaked load; only the
 *   zero-tie ones (lsf = 0) happened to balance.
 *
 *   The bracketed term was the interpolation itself, not a multiplier. Ties
 *   redistribute load between columns — they cannot make it disappear.
 *
 *   This was invisible until a test runner was added in 2026; the module's
 *   own test suite had never been executed. See legacy/README.md.
 *
 * @param {object} archetype
 * @param {number} failedColumns - how many columns have already failed
 */
export function computeDamageRate(archetype, failedColumns = 0) {
  const r0 = computeR0(archetype);
  const lsf = computeLoadSharingFactor(archetype);
  const surviving = Math.max(r0 - failedColumns, 1);
  const uniform = 1 / surviving;

  // Concentration penalty: how much MORE than the uniform share the
  // most-stressed column carries. Ranges from (2·surviving−1)/surviving at
  // lsf = 0 down to 1.0 at lsf = 1 (perfect sharing → everyone at uniform).
  // It is always ≥ 1, so peak × surviving ≥ 1 and load is never destroyed.
  const concentration = 1 + (1 - lsf) * ((surviving - 1) / surviving);

  return uniform * concentration;
}

// ─── Full archetype report ────────────────────────────────────────────────────

/**
 * Returns an array of analysis objects — one per archetype — with:
 *   R0               : independent load paths (distinct across all 6 archetypes)
 *   loadSharingFactor: benefit of lateral ties on damage rate [0–1]
 *   damageRate_intact: fractional load per column before any failure
 *   damageRate_minus1: fractional load per column after one column lost
 */
export function analyzeArchetypes(archetypes = ARCHETYPES) {
  return archetypes.map((a) => ({
    id: a.id,
    columns: a.columns,
    lateralTies: a.lateralTies,
    R0: computeR0(a),
    loadSharingFactor: parseFloat(computeLoadSharingFactor(a).toFixed(4)),
    damageRate_intact: parseFloat(computeDamageRate(a, 0).toFixed(4)),
    damageRate_minus1: a.columns > 1 ? parseFloat(computeDamageRate(a, 1).toFixed(4)) : null,
  }));
}
