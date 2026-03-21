// src/logic/mycelialGrowth.js

/**
 * Mycelium-inspired regrowth mechanism.
 * When a node fails, try to grow a new path to a nearby viable node.
 */

export function growMycelialLink(failedNode, neighbors, decayMap, attempts = 3) {
  if (!failedNode || !Array.isArray(neighbors)) return null;

  let viableNodes = neighbors
    .filter(n => !decayMap.has(n.id) && n.healable)
    .sort((a, b) => b.signalStrength - a.signalStrength);

  let regrowthLinks = [];

  for (let i = 0; i < Math.min(attempts, viableNodes.length); i++) {
    const candidate = viableNodes[i];
    regrowthLinks.push({
      from: failedNode.id,
      to: candidate.id,
      strength: Math.min(failedNode.strength, candidate.strength) * 0.7,
      type: 'mycelial-link',
      establishedAt: Date.now()
    });
  }

  return regrowthLinks;
}
