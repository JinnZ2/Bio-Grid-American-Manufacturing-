// src/adapters/sensorAdapter.js

/**
 * Simulated Sensor Adapter
 * This adapter pulls mock sensor data from a local file.
 * Replace this with real APIs or GPIO reads when you're off your phone and into hardware land.
 */

export async function fetchSensorData() {
  try {
    const res = await fetch('/data/sensors.json');
    if (!res.ok) throw new Error('Failed to fetch sensor data');
    const data = await res.json();
    return data;
  } catch (err) {
    console.warn('⚠️ Using fallback sensor data:', err);
    return [
      {
        id: "sensor_air_01",
        type: "air_quality",
        value: 0.87,
        location: "Node-3",
        timestamp: Date.now()
      },
      {
        id: "sensor_temp_07",
        type: "temperature",
        value: 22.3,
        location: "Node-5",
        timestamp: Date.now()
      }
    ];
  }
}
