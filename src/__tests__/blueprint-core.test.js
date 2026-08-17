import { blueprintCore } from '../technical/blueprint-core';

describe('blueprintCore', () => {
  test('PHI matches golden ratio', () => {
    expect(blueprintCore.PHI).toBeCloseTo((1 + Math.sqrt(5)) / 2, 10);
  });

  test('GOLDEN_ANGLE is defined correctly', () => {
    expect(blueprintCore.GOLDEN_ANGLE).toBeCloseTo(137.508, 1);
  });

  test('voltage classes are ordered descending', () => {
    const voltages = blueprintCore.voltageClasses_kV;
    for (let i = 1; i < voltages.length; i++) {
      expect(voltages[i]).toBeLessThan(voltages[i - 1]);
    }
  });

  test('implementation phases sum to total', () => {
    const { phase1, phase2, phase3, total } = blueprintCore.implementationPhases;
    expect(phase1.$B + phase2.$B + phase3.$B).toBe(total.$B);
  });

  test('primary hub has required fields', () => {
    const primary = blueprintCore.centralHubs.primary;
    expect(primary).toHaveProperty('city');
    expect(primary).toHaveProperty('powerMW');
    expect(primary).toHaveProperty('GPUs');
    expect(primary).toHaveProperty('cooling');
  });

  test('edge deployment tiers use Fibonacci counts', () => {
    const { tier1, tier2, tier3 } = blueprintCore.edgeDeployment;
    expect(tier1.count).toBe(89);
    expect(tier2.count).toBe(233);
    expect(tier3.count).toBe(377);
  });

  test('sensor matrix total matches sum of categories', () => {
    const s = blueprintCore.sensorMatrix;
    expect(s.powerQuality + s.weather + s.thermal + s.vibration).toBe(s.totalSensors);
  });
});
