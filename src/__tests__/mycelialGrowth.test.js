// __tests__/mycelialGrowth.test.js

import { growMycelialLink } from '../src/logic/mycelialGrowth';

describe('growMycelialLink', () => {
  const failedNode = {
    id: 'node_fail',
    strength: 8,
  };

  const neighbors = [
    { id: 'n1', signalStrength: 5, healable: true },
    { id: 'n2', signalStrength: 7, healable: false },
    { id: 'n3', signalStrength: 9, healable: true },
    { id: 'n4', signalStrength: 6, healable: true },
  ];

  const decayMap = new Map();
  decayMap.set('n1', true); // simulate n1 is decayed

  it('should return regrowth links to viable neighbors only', () => {
    const links = growMycelialLink(failedNode, neighbors, decayMap, 2);

    expect(links.length).toBe(2);
    expect(links[0].from).toBe('node_fail');
    expect(links[0].type).toBe('mycelial-link');
    expect(links[0].strength).toBeLessThan(failedNode.strength);
    expect(links[0].to).toBe('n3'); // strongest viable
  });

  it('should return empty array if no viable neighbors', () => {
    const deadMap = new Map(neighbors.map(n => [n.id, true]));
    const links = growMycelialLink(failedNode, neighbors, deadMap, 3);
    expect(links).toEqual([]);
  });

  it('should return null for bad input', () => {
    expect(growMycelialLink(null, [], new Map())).toBeNull();
    expect(growMycelialLink(failedNode, null, new Map())).toBeNull();
  });
});
