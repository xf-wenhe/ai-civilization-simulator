import React from 'react';
import { Agent, Memory } from '../types';
import { PERSONALITY_LABELS } from '../constants';
import './AgentDetails.css';

interface AgentDetailsProps {
  agent: Agent | null;
  memories: Memory[];
  loading: boolean;
}

export const AgentDetails: React.FC<AgentDetailsProps> = ({ agent, memories, loading }) => {
  if (loading) {
    return <div className="agent-details-loading">Loading agent details...</div>;
  }

  if (!agent) {
    return <div className="agent-details-empty">Select an agent to view details</div>;
  }

  const personality = agent.personality || {};
  const goals = agent.goals || [];

  return (
    <div className="agent-details">
      <h2 className="details-title">{agent.name}</h2>

      <section className="details-section">
        <h3>Personality</h3>
        <div className="personality-grid">
          {Object.entries(personality).map(([trait, value]) => (
            <div key={trait} className="personality-item">
              <label>{PERSONALITY_LABELS[trait] || trait}</label>
              <div className="personality-bar">
                <div
                  className="personality-fill"
                  style={{ width: `${(value as number) * 100}%` }}
                />
              </div>
              <span>{((value as number) * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </section>

      <section className="details-section">
        <h3>Goals</h3>
        <div className="goals-list">
          {goals.map((goal, index) => (
            <div
              key={index}
              className={`goal-item ${goal.completed ? 'completed' : ''}`}
            >
              <span className="goal-priority">{(goal.priority * 100).toFixed(0)}%</span>
              <span className="goal-description">{goal.description}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="details-section">
        <h3>Skills</h3>
        <div className="skills-list">
          {agent.skills && Object.entries(agent.skills).map(([skill, level]) => (
            <div key={skill} className="skill-item">
              <label>{skill}</label>
              <div className="skill-bar">
                <div className="skill-fill" style={{ width: `${(level as number) * 100}%` }} />
              </div>
              <span>{((level as number) * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </section>

      <section className="details-section">
        <h3>Recent Memories</h3>
        <div className="memories-list">
          {memories.length === 0 ? (
            <div className="no-memories">No memories yet</div>
          ) : (
            memories.slice(0, 10).map((memory, index) => (
              <div key={index} className="memory-item">
                <div className="memory-header">
                  <span className="memory-type">{memory.memory_type}</span>
                  <span className="memory-time">Tick {memory.timestamp}</span>
                </div>
                <div className="memory-content">{memory.content}</div>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
};