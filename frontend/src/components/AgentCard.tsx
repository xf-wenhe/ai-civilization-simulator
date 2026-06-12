import React from 'react';
import { Agent } from '../types';
import { ACTION_COLORS } from '../constants';
import './AgentCard.css';

interface AgentCardProps {
  agent: Agent;
  isSelected: boolean;
  onClick: () => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent, isSelected, onClick }) => {
  const actionColor = agent.current_action
    ? ACTION_COLORS[agent.current_action] || '#999'
    : '#999';

  return (
    <div
      className={`agent-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      style={{ borderLeft: `4px solid ${actionColor}` }}
    >
      <div className="agent-header">
        <h3 className="agent-name">{agent.name}</h3>
        <span className="agent-id">#{agent.id.split('_')[1]}</span>
      </div>

      <div className="agent-position">
        📍 ({agent.position[0]}, {agent.position[1]})
      </div>

      <div className="agent-status">
        <div className="status-bar">
          <label>健康值</label>
          <div className="bar">
            <div className="bar-fill health" style={{ width: `${agent.health}%` }} />
          </div>
          <span>{agent.health.toFixed(0)}%</span>
        </div>

        <div className="status-bar">
          <label>能量值</label>
          <div className="bar">
            <div className="bar-fill energy" style={{ width: `${agent.energy}%` }} />
          </div>
          <span>{agent.energy.toFixed(0)}%</span>
        </div>
      </div>

      {agent.current_action && (
        <div className="agent-action" style={{ color: actionColor }}>
          ⚡ {agent.current_action.toUpperCase()}
        </div>
      )}

      {Object.keys(agent.inventory).length > 0 && (
        <div className="agent-inventory">
          {Object.entries(agent.inventory).map(([resource, count]) => (
            <span key={resource} className="inventory-item">
              {resource}: {count}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};