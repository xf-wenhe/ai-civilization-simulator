import React from 'react';
import { WorldMap, Agent } from '../types';
import { BIOME_COLORS } from '../constants';
import './WorldMapComponent.css';

interface WorldMapComponentProps {
  worldMap: WorldMap | null;
  agents: Agent[];
  selectedAgentId: string | null;
  onCellClick: (position: [number, number]) => void;
}

export const WorldMapComponent: React.FC<WorldMapComponentProps> = ({
  worldMap,
  agents,
  selectedAgentId,
  onCellClick,
}) => {
  if (!worldMap) {
    return <div className="map-loading">Loading map...</div>;
  }

  const cellSize = 12;
  const width = worldMap.width * cellSize;
  const height = worldMap.height * cellSize;

  // Create agent position map for quick lookup
  const agentPositions = new Map<string, Agent>();
  agents.forEach((agent) => {
    agentPositions.set(`${agent.position[0]},${agent.position[1]}`, agent);
  });

  const renderCell = (x: number, y: number) => {
    const key = `${x},${y}`;
    const location = worldMap.locations[key];
    const agent = agentPositions.get(key);

    if (!location) return null;

    const backgroundColor = BIOME_COLORS[location.biome] || '#999';
    const isSelected = agent && agent.id === selectedAgentId;

    return (
      <div
        key={key}
        className={`map-cell ${isSelected ? 'selected' : ''}`}
        style={{
          left: x * cellSize,
          top: y * cellSize,
          width: cellSize,
          height: cellSize,
          backgroundColor,
        }}
        onClick={() => onCellClick([x, y])}
      >
        {agent && (
          <div
            className="agent-marker"
            style={{
              backgroundColor: isSelected ? '#FFD700' : '#FF4500',
              boxShadow: isSelected ? '0 0 8px #FFD700' : 'none',
            }}
          />
        )}
      </div>
    );
  };

  return (
    <div className="world-map-container">
      <h3 className="map-title">World Map</h3>
      <div className="map-legend">
        {Object.entries(BIOME_COLORS).map(([biome, color]) => (
          <div key={biome} className="legend-item">
            <div className="legend-color" style={{ backgroundColor: color }} />
            <span>{biome}</span>
          </div>
        ))}
      </div>
      <div
        className="world-map"
        style={{ width, height }}
      >
        {Array.from({ length: worldMap.width }, (_, x) =>
          Array.from({ length: worldMap.height }, (_, y) => renderCell(x, y))
        )}
      </div>
    </div>
  );
};