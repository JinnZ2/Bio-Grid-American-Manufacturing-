// src/components/LiveStatusPanel.jsx

import React from 'react';

const LiveStatusPanel = ({ swarmMetrics, knowledgeNodes, sensors }) => {
  return (
    <div className="p-4 bg-gray-900 text-white rounded-lg shadow-md w-full md:w-1/3">
      <h2 className="text-lg font-bold mb-2">📡 Live Status Panel</h2>

      <div className="text-sm space-y-2">
        <div>🧠 <strong>Convergence:</strong> {swarmMetrics.convergence.toFixed(1)}%</div>
        <div>📊 <strong>Efficiency:</strong> {swarmMetrics.efficiency.toFixed(1)}%</div>
        <div>📍 <strong>Discovered Nodes:</strong> {knowledgeNodes.filter(n => n.discovered).length} / {knowledgeNodes.length}</div>
        <div>📡 <strong>Live Sensors:</strong> {sensors.length}</div>
      </div>

      <hr className="my-3 border-gray-700" />

      <div className="space-y-1 max-h-48 overflow-y-auto text-xs">
        {sensors.map((s, idx) => (
          <div key={idx} className="bg-gray-800 px-2 py-1 rounded flex justify-between items-center">
            <span>{s.type} @ {s.location}</span>
            <span className="text-green-400">{s.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LiveStatusPanel;
