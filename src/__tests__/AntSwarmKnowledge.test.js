import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AntSwarmKnowledge from '../components/AntSwarmKnowledge';

// Return a stable config reference
const mockConfig = {
  num_ants: 5,
  ant_roles: ['scout', 'worker'],
  discovery_radius: 30,
  pheromone_strength: 0.5,
  pheromone_decay: 0.01,
  swarm_refresh_rate: 100,
  ant_speed: 2,
  randomness_factor: 0.3,
  max_memory_length: 20,
};

jest.mock('../hooks/useSwarmConfig', () => ({
  useSwarmConfig: () => mockConfig,
}));

// Mock canvas
const mockCtx = {
  clearRect: jest.fn(),
  beginPath: jest.fn(),
  arc: jest.fn(),
  fill: jest.fn(),
  stroke: jest.fn(),
  moveTo: jest.fn(),
  lineTo: jest.fn(),
  fillText: jest.fn(),
  fillStyle: '',
  strokeStyle: '',
  lineWidth: 1,
  font: '',
  textAlign: '',
};

beforeAll(() => {
  HTMLCanvasElement.prototype.getContext = jest.fn(() => mockCtx);
});

describe('AntSwarmKnowledge', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render with start button', () => {
    render(<AntSwarmKnowledge />);
    expect(screen.getByText(/Start Swarm/)).toBeTruthy();
  });

  it('should render metrics display', () => {
    render(<AntSwarmKnowledge />);
    expect(screen.getByText(/Total Paths/)).toBeTruthy();
    expect(screen.getByText(/Efficiency/)).toBeTruthy();
    expect(screen.getByText(/Knowledge:/)).toBeTruthy();
    expect(screen.getByText(/Convergence/)).toBeTruthy();
  });

  it('should toggle to pause when started', () => {
    render(<AntSwarmKnowledge />);
    const startBtn = screen.getByText(/Start Swarm/);
    fireEvent.click(startBtn);
    expect(screen.getByText(/Pause Swarm/)).toBeTruthy();
  });

  it('should reset state when reset clicked', () => {
    render(<AntSwarmKnowledge />);
    fireEvent.click(screen.getByText(/Start Swarm/));
    fireEvent.click(screen.getByText(/Reset/));
    expect(screen.getByText(/Start Swarm/)).toBeTruthy();
  });

  it('should render canvas element', () => {
    const { container } = render(<AntSwarmKnowledge />);
    const canvas = container.querySelector('canvas');
    expect(canvas).toBeTruthy();
    expect(canvas.width).toBe(800);
    expect(canvas.height).toBe(500);
  });

  it('should call canvas getContext on render', () => {
    render(<AntSwarmKnowledge />);
    expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalledWith('2d');
  });

  it('should draw to canvas after initialization', () => {
    render(<AntSwarmKnowledge />);
    expect(mockCtx.clearRect).toHaveBeenCalled();
    expect(mockCtx.fillText).toHaveBeenCalledWith('NEST', 400, 255);
  });
});
