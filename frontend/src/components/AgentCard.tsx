import React from 'react';
import { Agent } from '../types';
import { ACTION_COLORS } from '../constants';
import { SurvivalBars } from './SurvivalBars';
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

      <SurvivalBars
        health={agent.health}
        energy={agent.energy}
        hunger={agent.hunger}
        thirst={agent.thirst}
      />

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

      {(agent.spouse_id || agent.children.length > 0) && (
        <div className="agent-family">
          {agent.spouse_id && (
            <div className="agent-family-item">
              💑 配偶: #{agent.spouse_id.split('_')[1]}
            </div>
          )}
          {agent.children.length > 0 && (
            <div className="agent-family-item">
              👶 孩子: {agent.children.map(childId => `#${childId.split('_')[1]}`).join(', ')}
            </div>
          )}
        </div>
      )}
    </div>
  );
};