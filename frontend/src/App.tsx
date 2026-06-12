import React, { useState, useEffect } from 'react';
import { useAgents, useWorldState, useWorldMap } from './hooks/useApi';
import { AgentCard } from './components/AgentCard';
import { WorldMapComponent } from './components/WorldMapComponent';
import { AgentDetails } from './components/AgentDetails';
import { Agent, Memory } from './types';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const { agents, loading: agentsLoading } = useAgents();
  const { worldState, loading: worldLoading } = useWorldState();
  const { worldMap, loading: mapLoading } = useWorldMap();

  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [agentMemories, setAgentMemories] = useState<Memory[]>([]);
  const [events, setEvents] = useState<string[]>([]);

  const selectedAgent = agents.find((a) => a.id === selectedAgentId) || null;

  // Fetch agent memories when selection changes
  useEffect(() => {
    if (!selectedAgentId) {
      setAgentMemories([]);
      return;
    }

    const fetchMemories = async () => {
      try {
        const response = await fetch(`${API_BASE}/agents/${selectedAgentId}/memories`);
        const data = await response.json();
        setAgentMemories(data.memories || []);
      } catch (error) {
        console.error('Failed to fetch memories:', error);
      }
    };

    fetchMemories();
  }, [selectedAgentId]);

  // Fetch recent events
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch(`${API_BASE}/events?limit=20`);
        const data = await response.json();
        setEvents(data.events || []);
      } catch (error) {
        console.error('Failed to fetch events:', error);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleCellClick = (position: [number, number]) => {
    // Find agent at this position
    const agentAtPos = agents.find((a) => {
      return a.position[0] === position[0] && a.position[1] === position[1];
    });

    if (agentAtPos) {
      setSelectedAgentId(agentAtPos.id);
    }
  };

  if (agentsLoading || worldLoading) {
    return <div className="loading">Loading civilization...</div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🏛️ AI Civilization Simulator</h1>
        {worldState && (
          <div className="world-info">
            <span>Day {worldState.day}</span>
            <span>Tick {worldState.tick}</span>
            <span>{worldState.time_of_day.toFixed(1)}h</span>
            <span className="weather">{worldState.weather}</span>
          </div>
        )}
      </header>

      <div className="app-content">
        <aside className="sidebar-left">
          <div className="agents-panel">
            <h2>Agents ({agents.length})</h2>
            <div className="agents-list">
              {agents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  isSelected={agent.id === selectedAgentId}
                  onClick={() => setSelectedAgentId(agent.id)}
                />
              ))}
            </div>
          </div>
        </aside>

        <main className="main-content">
          <WorldMapComponent
            worldMap={worldMap}
            agents={agents}
            selectedAgentId={selectedAgentId}
            onCellClick={handleCellClick}
          />

          <div className="events-panel">
            <h3>Recent Events</h3>
            <div className="events-list">
              {events.map((event, index) => (
                <div key={index} className="event-item">
                  {event}
                </div>
              ))}
            </div>
          </div>
        </main>

        <aside className="sidebar-right">
          <AgentDetails
            agent={selectedAgent}
            memories={agentMemories}
            loading={false}
          />
        </aside>
      </div>
    </div>
  );
}

export default App;