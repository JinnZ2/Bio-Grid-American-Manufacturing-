// __tests__/sensorAdapter.test.js

import { fetchSensorData } from '../adapters/sensorAdapter';

describe('fetchSensorData', () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it('should return parsed sensor data on successful fetch', async () => {
    const mockData = [
      { id: 'sensor_01', type: 'air_quality', value: 0.95, location: 'Node-1', timestamp: 1000 },
    ];

    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockData),
      })
    );

    const result = await fetchSensorData();
    expect(result).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith('/data/sensors.json');
  });

  it('should return fallback data when fetch fails', async () => {
    global.fetch = jest.fn(() => Promise.reject(new Error('Network error')));

    const result = await fetchSensorData();
    expect(result).toHaveLength(2);
    expect(result[0].id).toBe('sensor_air_01');
    expect(result[0].type).toBe('air_quality');
    expect(result[1].id).toBe('sensor_temp_07');
    expect(result[1].type).toBe('temperature');
  });

  it('should return fallback data when response is not ok', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        status: 404,
      })
    );

    const result = await fetchSensorData();
    expect(result).toHaveLength(2);
    expect(result[0].type).toBe('air_quality');
  });

  it('should include timestamps in fallback data', async () => {
    global.fetch = jest.fn(() => Promise.reject(new Error('fail')));

    const before = Date.now();
    const result = await fetchSensorData();
    const after = Date.now();

    result.forEach((sensor) => {
      expect(sensor.timestamp).toBeGreaterThanOrEqual(before);
      expect(sensor.timestamp).toBeLessThanOrEqual(after);
    });
  });
});
