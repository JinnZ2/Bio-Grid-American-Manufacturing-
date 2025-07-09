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


### 
Example Usage:

Drop this into your swarm update cycle or failover handler:

import { growMycelialLink } from './logic/mycelialGrowth';

const regrowth = growMycelialLink(failedNode, nearbyNodes, decayMap, 5);
if (regrowth && regrowth.length > 0) {
  // Store these in your pheromone trail system or route planner
  setMycelialLinks(prev => [...prev, ...regrowth]);
}

Visualizing (optional)
	•	Use dotted purple lines for type === 'mycelial-link'
	•	Decay them if unused over time
	•	Reinforce if ants adopt the route ###
