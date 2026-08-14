import { mycelialNetwork } from '../technical/mycelial-network';

describe('mycelialNetwork', () => {
  test('underground network length is positive', () => {
    expect(mycelialNetwork.undergroundLength_km).toBeGreaterThan(0);
  });

  test('underwater crossings have required fields', () => {
    const crossings = mycelialNetwork.underwaterCrossings;
    Object.values(crossings).forEach((crossing) => {
      expect(crossing).toHaveProperty('from');
      expect(crossing).toHaveProperty('to');
      expect(crossing).toHaveProperty('length_km');
      expect(crossing).toHaveProperty('depth_m');
    });
  });

  test('Lake Superior is the longest crossing', () => {
    const { lakeMichigan, lakeErie, lakeSuperior } = mycelialNetwork.underwaterCrossings;
    expect(lakeSuperior.length_km).toBeGreaterThan(lakeMichigan.length_km);
    expect(lakeSuperior.length_km).toBeGreaterThan(lakeErie.length_km);
  });

  test('construction methods include standard techniques', () => {
    expect(mycelialNetwork.constructionMethods).toContain('HDD');
    expect(mycelialNetwork.constructionMethods).toContain('TBM');
  });

  test('fiber cable spec has high capacity', () => {
    expect(mycelialNetwork.cableSpecs.fiber.fibers).toBe(288);
  });

  test('protection includes thermal monitoring', () => {
    expect(mycelialNetwork.protection.thermalMonitoring).toBe(true);
  });

  test('environmental mitigation covers key areas', () => {
    const mitigation = mycelialNetwork.protection.environmentalMitigation;
    expect(mitigation).toContain('wetlands');
    expect(mitigation).toContain('wildlife');
    expect(mitigation).toContain('waterResources');
  });
});
