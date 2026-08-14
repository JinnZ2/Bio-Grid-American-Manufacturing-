import { renderHook, waitFor } from '@testing-library/react';
import { useSwarmConfig } from '../hooks/useSwarmConfig';

describe('useSwarmConfig', () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it('should return null initially', () => {
    global.fetch = jest.fn(() => new Promise(() => {}));
    const { result } = renderHook(() => useSwarmConfig());
    expect(result.current).toBeNull();
  });

  it('should return config after successful fetch', async () => {
    const mockConfig = {
      num_ants: 75,
      ant_roles: ['scout', 'worker', 'forager'],
      discovery_radius: 30,
    };

    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockConfig),
      })
    );

    const { result } = renderHook(() => useSwarmConfig());

    await waitFor(() => {
      expect(result.current).toEqual(mockConfig);
    });

    expect(global.fetch).toHaveBeenCalledWith('/config/parameters.json');
  });

  it('should return defaults when fetch fails', async () => {
    global.fetch = jest.fn(() => Promise.reject(new Error('Network error')));

    const { result } = renderHook(() => useSwarmConfig());

    await waitFor(() => {
      expect(result.current).not.toBeNull();
    });

    expect(result.current.num_ants).toBe(50);
    expect(result.current.ant_roles).toEqual(['scout', 'worker', 'forager']);
    expect(result.current.discovery_radius).toBe(30);
    expect(result.current.swarm_refresh_rate).toBe(100);
  });
});
