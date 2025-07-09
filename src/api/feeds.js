// src/api/feeds.js

export async function loadKnowledgeNodes() {
  try {
    const response = await fetch('/config/knowledge_nodes.json');
    if (!response.ok) throw new Error('Failed to load node data');

    const nodes = await response.json();

    return nodes.map(n => ({
      ...n,
      discovered: false
    }));
  } catch (err) {
    console.warn('⚠️ Using fallback static nodes due to error:', err);

    // Static fallback
    return [
      { id: 1, x: 100, y: 100, value: 'Pattern Recognition', strength: 8, discovered: false },
      { id: 2, x: 400, y: 150, value: 'Network Analysis', strength: 6, discovered: false },
      { id: 3, x: 600, y: 300, value: 'Emergent Behavior', strength: 9, discovered: false },
      { id: 4, x: 200, y: 400, value: 'Distributed Learning', strength: 7, discovered: false },
      { id: 5, x: 500, y: 450, value: 'Collective Intelligence', strength: 10, discovered: false },
      { id: 6, x: 750, y: 100, value: 'Self Organization', strength: 8, discovered: false }
    ];
  }
}
