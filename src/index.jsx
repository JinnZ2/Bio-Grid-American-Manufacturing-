import React from 'react';
import { createRoot } from 'react-dom/client';
import AntSwarmKnowledge from './components/AntSwarmKnowledge';
import LiveStatusPanel from './components/LiveStatusPanel';

const App = () => (
  <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem', fontFamily: 'system-ui' }}>
    <h1 style={{ color: '#58a6ff' }}>BioGrid 2.0 Dashboard</h1>
    <p style={{ color: '#8b949e' }}>
      Decentralized manufacturing intelligence &mdash; Great Lakes Region
    </p>
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '1.5rem' }}>
      <AntSwarmKnowledge />
      <LiveStatusPanel />
    </div>
  </div>
);

const container = document.getElementById('root');
if (container) {
  createRoot(container).render(<App />);
}

export default App;
