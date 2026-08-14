import {
  ARCHETYPES,
  computeR0,
  computeLoadSharingFactor,
  computeDamageRate,
  analyzeArchetypes,
} from '../logic/archetypeRedundancy';

describe('archetypeRedundancy — graph-theory correctness', () => {
  // ─── R0 must be distinct across all 6 archetypes ──────────────────────────

  it('R0 values are NOT all identical (regression: prior bug collapsed them)', () => {
    const r0s = ARCHETYPES.map(computeR0);
    const unique = new Set(r0s).size;
    expect(unique).toBeGreaterThan(1);
  });

  it('each archetype has R0 equal to its column count', () => {
    ARCHETYPES.forEach((a) => {
      expect(computeR0(a)).toBe(a.columns);
    });
  });

  it('lateral ties do NOT change R0 — braced-dual and dual-parallel share R0=2', () => {
    const dual = ARCHETYPES.find((a) => a.id === 'dual-parallel');
    const braced = ARCHETYPES.find((a) => a.id === 'braced-dual');
    expect(computeR0(dual)).toBe(2);
    expect(computeR0(braced)).toBe(2);
    // Same R0, different damage rates — that is the correct model
  });

  // ─── Load sharing factor ───────────────────────────────────────────────────

  it('no lateral ties → loadSharingFactor = 0', () => {
    const dual = ARCHETYPES.find((a) => a.id === 'dual-parallel');
    expect(computeLoadSharingFactor(dual)).toBe(0);
  });

  it('lateral ties → loadSharingFactor > 0', () => {
    const braced = ARCHETYPES.find((a) => a.id === 'braced-dual');
    expect(computeLoadSharingFactor(braced)).toBeGreaterThan(0);
  });

  it('loadSharingFactor stays in [0, 1]', () => {
    ARCHETYPES.forEach((a) => {
      const lsf = computeLoadSharingFactor(a);
      expect(lsf).toBeGreaterThanOrEqual(0);
      expect(lsf).toBeLessThanOrEqual(1);
    });
  });

  it('single-column loadSharingFactor = 0 (no neighbours to share with)', () => {
    const single = ARCHETYPES.find((a) => a.id === 'single-column');
    expect(computeLoadSharingFactor(single)).toBe(0);
  });

  // ─── Damage rate ───────────────────────────────────────────────────────────

  // Corrected 2026. This previously compared the two archetypes at
  // failedColumns = 1, where both drop to a single surviving column. With one
  // column left there is nobody to share with, so ties cannot help and both
  // return exactly 1.0 — the assertion contradicted the module's own thesis
  // that lateral ties add no independent load path. The intent ("ties help")
  // is right; it just has to be measured where sharing can act.
  it('braced-dual has lower damage rate than dual-parallel while both columns stand', () => {
    const dual = ARCHETYPES.find((a) => a.id === 'dual-parallel');
    const braced = ARCHETYPES.find((a) => a.id === 'braced-dual');
    expect(computeDamageRate(braced, 0)).toBeLessThan(computeDamageRate(dual, 0));
  });

  it('ties provide no benefit once only one column survives', () => {
    const dual = ARCHETYPES.find((a) => a.id === 'dual-parallel');
    const braced = ARCHETYPES.find((a) => a.id === 'braced-dual');
    expect(computeDamageRate(braced, 1)).toBe(computeDamageRate(dual, 1));
    expect(computeDamageRate(braced, 1)).toBe(1);
  });

  it('load is conserved — peak column load × survivors is never below total', () => {
    for (const a of ARCHETYPES) {
      for (let failed = 0; failed < a.columns; failed++) {
        const surviving = Math.max(a.columns - failed, 1);
        const peak = computeDamageRate(a, failed);
        // Peak ≥ uniform share, so the survivors together account for all load.
        expect(peak * surviving).toBeGreaterThanOrEqual(1 - 1e-9);
        expect(peak).toBeGreaterThanOrEqual(1 / surviving - 1e-9);
      }
    }
  });

  it('damage rate rises when columns fail', () => {
    const full = ARCHETYPES.find((a) => a.id === 'full-grid');
    expect(computeDamageRate(full, 1)).toBeGreaterThan(computeDamageRate(full, 0));
    expect(computeDamageRate(full, 2)).toBeGreaterThan(computeDamageRate(full, 1));
  });

  it('damage rate never exceeds 1.0', () => {
    ARCHETYPES.forEach((a) => {
      for (let failed = 0; failed < a.columns; failed++) {
        expect(computeDamageRate(a, failed)).toBeLessThanOrEqual(1.0);
      }
    });
  });

  // ─── Full report ───────────────────────────────────────────────────────────

  it('analyzeArchetypes returns one record per archetype', () => {
    const report = analyzeArchetypes();
    expect(report).toHaveLength(ARCHETYPES.length);
  });

  it('all six archetype R0 values are present in the report', () => {
    const report = analyzeArchetypes();
    const r0s = report.map((r) => r.R0);
    expect(r0s).toContain(1);
    expect(r0s).toContain(2);
    expect(r0s).toContain(3);
    expect(r0s).toContain(4);
    // Must NOT be all the same value
    expect(new Set(r0s).size).toBeGreaterThan(1);
  });
});
