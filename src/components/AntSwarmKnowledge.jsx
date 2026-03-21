import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Network } from 'lucide-react';
import { useSwarmConfig } from '../hooks/useSwarmConfig';

const AntSwarmKnowledge = () => {
  const canvasRef = useRef(null);
  const [isRunning, setIsRunning] = useState(false);
  const [ants, setAnts] = useState([]);
  const [knowledgeNodes, setKnowledgeNodes] = useState([]);
  const [discoveries, setDiscoveries] = useState([]);
  const [swarmIntelligence, setSwarmIntelligence] = useState({
    totalPaths: 0,
    efficiency: 0,
    knowledge: 0,
    convergence: 0,
  });

  const config = useSwarmConfig();

  // Use refs to avoid stale closures in the simulation loop
  const antsRef = useRef([]);
  const nodesRef = useRef([]);
  const discoveriesRef = useRef([]);

  // Initialize knowledge landscape
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !config) return;

    const nodes = [
      { id: 1, x: 100, y: 100, value: 'Pattern Recognition', strength: 8, discovered: false },
      { id: 2, x: 400, y: 150, value: 'Network Analysis', strength: 6, discovered: false },
      { id: 3, x: 600, y: 300, value: 'Emergent Behavior', strength: 9, discovered: false },
      { id: 4, x: 200, y: 400, value: 'Distributed Learning', strength: 7, discovered: false },
      { id: 5, x: 500, y: 450, value: 'Collective Intelligence', strength: 10, discovered: false },
      { id: 6, x: 750, y: 100, value: 'Self Organization', strength: 8, discovered: false },
    ];

    const roles = config.ant_roles || ['scout', 'worker', 'forager'];
    const numAnts = config.num_ants || 75;
    const speed = config.ant_speed || 2;

    const antColony = Array.from({ length: numAnts }, (_, i) => ({
      id: i,
      x: 400,
      y: 250,
      vx: (Math.random() - 0.5) * speed,
      vy: (Math.random() - 0.5) * speed,
      carrying: null,
      energy: 100,
      memory: [],
      role: roles[Math.floor(Math.random() * roles.length)],
      knowledge: 0,
    }));

    antsRef.current = antColony;
    nodesRef.current = nodes;
    discoveriesRef.current = [];
    setKnowledgeNodes(nodes);
    setAnts(antColony);
    setDiscoveries([]);
  }, [config]);

  const updateSwarm = useCallback(() => {
    const currentAnts = antsRef.current;
    const currentNodes = nodesRef.current;
    const discoveryRadius = config?.discovery_radius || 30;
    const speed = config?.ant_speed || 2;
    const randomness = config?.randomness_factor || 0.3;
    const maxMemory = config?.max_memory_length || 20;

    const newDiscoveries = [];

    const newAnts = currentAnts.map((ant) => {
      const newAnt = { ...ant, memory: [...ant.memory] };

      let nearestNode = null;
      let minDistance = Infinity;

      currentNodes.forEach((node) => {
        const dist = Math.sqrt((ant.x - node.x) ** 2 + (ant.y - node.y) ** 2);
        if (dist < minDistance && !node.discovered) {
          minDistance = dist;
          nearestNode = node;
        }
      });

      if (nearestNode && minDistance < discoveryRadius && !nearestNode.discovered) {
        const nodeIndex = currentNodes.findIndex((n) => n.id === nearestNode.id);
        currentNodes[nodeIndex] = { ...currentNodes[nodeIndex], discovered: true };
        nearestNode = currentNodes[nodeIndex];
        newDiscoveries.push({
          node: nearestNode,
          discoverer: ant.id,
          time: Date.now(),
          role: ant.role,
        });
        newAnt.knowledge += nearestNode.strength;
        newAnt.carrying = nearestNode.value;
      }

      if (nearestNode) {
        const dx = nearestNode.x - ant.x;
        const dy = nearestNode.y - ant.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 0) {
          newAnt.vx = (dx / distance) * speed + (Math.random() - 0.5) * randomness;
          newAnt.vy = (dy / distance) * speed + (Math.random() - 0.5) * randomness;
        }
      } else {
        newAnt.vx += (Math.random() - 0.5) * randomness;
        newAnt.vy += (Math.random() - 0.5) * randomness;
      }

      newAnt.x += newAnt.vx;
      newAnt.y += newAnt.vy;

      newAnt.x = Math.max(0, Math.min(800, newAnt.x));
      newAnt.y = Math.max(0, Math.min(500, newAnt.y));
      if (newAnt.x <= 0 || newAnt.x >= 800) newAnt.vx *= -1;
      if (newAnt.y <= 0 || newAnt.y >= 500) newAnt.vy *= -1;

      newAnt.memory.push({ x: newAnt.x, y: newAnt.y, timestamp: Date.now() });
      if (newAnt.memory.length > maxMemory) newAnt.memory.shift();

      return newAnt;
    });

    // Update refs
    antsRef.current = newAnts;
    if (newDiscoveries.length > 0) {
      discoveriesRef.current = [...discoveriesRef.current, ...newDiscoveries];
    }

    // Compute metrics from fresh data
    const totalKnowledge = newAnts.reduce((sum, a) => sum + a.knowledge, 0);
    const discoveredCount = currentNodes.filter((n) => n.discovered).length;
    const nodeCount = currentNodes.length;

    // Sync to React state for rendering
    setAnts(newAnts);
    setKnowledgeNodes([...currentNodes]);
    if (newDiscoveries.length > 0) {
      setDiscoveries([...discoveriesRef.current]);
    }
    setSwarmIntelligence({
      totalPaths: newAnts.reduce((sum, a) => sum + a.memory.length, 0),
      efficiency: nodeCount > 0 ? Math.min(100, (discoveredCount / nodeCount) * 100) : 0,
      knowledge: totalKnowledge,
      convergence: nodeCount > 0 ? Math.min(100, (discoveredCount / nodeCount) * 100) : 0,
    });
  }, [config]);

  // Canvas rendering
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ants.forEach((ant) => {
      if (ant.memory.length > 1) {
        ctx.strokeStyle = `rgba(255, 165, 0, ${ant.knowledge / 100})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ant.memory.forEach((point, i) => {
          if (i === 0) ctx.moveTo(point.x, point.y);
          else ctx.lineTo(point.x, point.y);
        });
        ctx.stroke();
      }
    });

    knowledgeNodes.forEach((node) => {
      ctx.fillStyle = node.discovered ? '#10B981' : '#3B82F6';
      ctx.beginPath();
      ctx.arc(node.x, node.y, 15 + node.strength * 2, 0, 2 * Math.PI);
      ctx.fill();

      ctx.fillStyle = 'white';
      ctx.font = '10px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(node.value.substring(0, 8), node.x, node.y + 3);
    });

    ants.forEach((ant) => {
      ctx.fillStyle = ant.carrying
        ? '#EF4444'
        : ant.role === 'scout'
          ? '#8B5CF6'
          : ant.role === 'worker'
            ? '#F59E0B'
            : '#06B6D4';
      ctx.beginPath();
      ctx.arc(ant.x, ant.y, ant.knowledge > 0 ? 4 : 2, 0, 2 * Math.PI);
      ctx.fill();
    });

    ctx.fillStyle = '#DC2626';
    ctx.beginPath();
    ctx.arc(400, 250, 20, 0, 2 * Math.PI);
    ctx.fill();
    ctx.fillStyle = 'white';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('NEST', 400, 255);
  }, [ants, knowledgeNodes]);

  useEffect(() => {
    if (!isRunning) return;
    const interval = setInterval(updateSwarm, config?.swarm_refresh_rate || 100);
    return () => clearInterval(interval);
  }, [isRunning, updateSwarm, config]);

  return (
    <div className="p-4 bg-white shadow rounded">
      <h2 className="font-bold text-lg mb-2 flex items-center gap-2">
        <Network /> Ant Swarm Knowledge
      </h2>
      <div className="flex gap-2 mb-3">
        <button
          onClick={() => setIsRunning(!isRunning)}
          className={`px-4 py-2 rounded text-white font-medium ${isRunning ? 'bg-red-600' : 'bg-green-600'}`}
          disabled={!config}
        >
          {isRunning ? '⏸️ Pause Swarm' : '▶️ Start Swarm'}
        </button>
        <button
          onClick={() => {
            setIsRunning(false);
            setDiscoveries([]);
            setKnowledgeNodes((prev) => prev.map((n) => ({ ...n, discovered: false })));
          }}
          className="px-4 py-2 bg-gray-600 text-white rounded"
        >
          🔄 Reset
        </button>
      </div>
      <canvas ref={canvasRef} width={800} height={500} className="w-full bg-black rounded" />
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-700">
        <div>
          Total Paths: <strong>{swarmIntelligence.totalPaths}</strong>
        </div>
        <div>
          Efficiency: <strong>{swarmIntelligence.efficiency.toFixed(1)}%</strong>
        </div>
        <div>
          Knowledge: <strong>{swarmIntelligence.knowledge}</strong>
        </div>
        <div>
          Convergence: <strong>{swarmIntelligence.convergence.toFixed(1)}%</strong>
        </div>
      </div>
    </div>
  );
};

export default AntSwarmKnowledge;
