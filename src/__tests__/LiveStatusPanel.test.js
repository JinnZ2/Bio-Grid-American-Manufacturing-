import React from 'react';
import { render, screen } from '@testing-library/react';
import LiveStatusPanel from '../components/LiveStatusPanel';

describe('LiveStatusPanel', () => {
  const defaultProps = {
    swarmMetrics: { convergence: 45.5, efficiency: 72.3 },
    knowledgeNodes: [
      { id: 1, discovered: true },
      { id: 2, discovered: false },
      { id: 3, discovered: true },
    ],
    sensors: [
      { type: 'temperature', location: 'Node-1', value: '22.3C' },
      { type: 'air_quality', location: 'Node-3', value: '0.87' },
    ],
  };

  it('should render convergence and efficiency', () => {
    render(<LiveStatusPanel {...defaultProps} />);
    expect(screen.getByText(/45\.5%/)).toBeTruthy();
    expect(screen.getByText(/72\.3%/)).toBeTruthy();
  });

  it('should display discovered node count', () => {
    render(<LiveStatusPanel {...defaultProps} />);
    expect(screen.getByText(/2 \/ 3/)).toBeTruthy();
  });

  it('should display sensor count', () => {
    render(<LiveStatusPanel {...defaultProps} />);
    expect(screen.getByText(/Live Sensors/)).toBeTruthy();
  });

  it('should render each sensor entry', () => {
    render(<LiveStatusPanel {...defaultProps} />);
    expect(screen.getByText('22.3C')).toBeTruthy();
    expect(screen.getByText('0.87')).toBeTruthy();
  });

  it('should handle empty sensors array', () => {
    const props = { ...defaultProps, sensors: [] };
    const { container } = render(<LiveStatusPanel {...props} />);
    const sensorList = container.querySelector('.max-h-48');
    expect(sensorList.children.length).toBe(0);
  });
});
