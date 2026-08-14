// src/hooks/useSwarmConfig.js

import { useState, useEffect } from 'react';

export const useSwarmConfig = () => {
  const [config, setConfig] = useState(null);

  useEffect(() => {
    fetch('/config/parameters.json')
      .then(res => res.json())
      .then(setConfig)
      .catch(() => {
        console.warn('⚠️ Failed to load swarm config. Using defaults.');
        setConfig({
          num_ants: 50,
          ant_roles: ['scout', 'worker', 'forager'],
          discovery_radius: 30,
          pheromone_strength: 0.5,
          pheromone_decay: 0.01,
          swarm_refresh_rate: 100,
          ant_speed: 2,
          randomness_factor: 0.3
        });
      });
  }, []);

  return config;
};
