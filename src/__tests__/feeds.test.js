// __tests__/feeds.test.js

import { loadKnowledgeNodes } from '../api/feeds';

describe('loadKnowledgeNodes', () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it('should return nodes with discovered=false from successful fetch', async () => {
    const mockNodes = [
      { id: 1, x: 100, y: 100, value: 'Test Node', strength: 8 },
      { id: 2, x: 200, y: 200, value: 'Another Node', strength: 6 },
    ];

    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockNodes),
      })
    );

    const result = await loadKnowledgeNodes();
    expect(result).toHaveLength(2);
    result.forEach((node) => {
      expect(node.discovered).toBe(false);
    });
    expect(result[0].value).toBe('Test Node');
  });

  it('should preserve all original node properties', async () => {
    const mockNodes = [{ id: 1, x: 100, y: 200, value: 'Node', strength: 7 }];

    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockNodes),
      })
    );

    const result = await loadKnowledgeNodes();
    expect(result[0]).toEqual({
      id: 1,
      x: 100,
      y: 200,
      value: 'Node',
      strength: 7,
      discovered: false,
    });
  });

  it('should return 6 fallback nodes when fetch fails', async () => {
    global.fetch = jest.fn(() => Promise.reject(new Error('Network error')));

    const result = await loadKnowledgeNodes();
    expect(result).toHaveLength(6);
    result.forEach((node) => {
      expect(node).toHaveProperty('id');
      expect(node).toHaveProperty('x');
      expect(node).toHaveProperty('y');
      expect(node).toHaveProperty('value');
      expect(node).toHaveProperty('strength');
      expect(node.discovered).toBe(false);
    });
  });

  it('should return fallback nodes when response is not ok', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    );

    const result = await loadKnowledgeNodes();
    expect(result).toHaveLength(6);
    expect(result[0].value).toBe('Pattern Recognition');
    expect(result[4].value).toBe('Collective Intelligence');
  });

  it('should fetch from the correct endpoint', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([]),
      })
    );

    await loadKnowledgeNodes();
    expect(global.fetch).toHaveBeenCalledWith('/config/knowledge_nodes.json');
  });
});
