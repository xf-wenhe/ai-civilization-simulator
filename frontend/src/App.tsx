import { useState, useEffect } from 'react';
import { useAgents, useWorldState, useWorldMap } from './hooks/useApi';
import { AgentCard } from './components/AgentCard';
import { WorldMapComponent } from './components/WorldMapComponent';
import { AgentDetails } from './components/AgentDetails';
import { Agent, Memory } from './types';
import './App.css';

const API_BASE = 'http://localhost:8888';

function App() {
  const { agents, loading: agentsLoading } = useAgents();
  const { worldState, loading: worldLoading } = useWorldState();
  const { worldMap, loading: mapLoading } = useWorldMap();

  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [selectedAgentDetails, setSelectedAgentDetails] = useState<Agent | null>(null);
  const [agentMemories, setAgentMemories] = useState<Memory[]>([]);
  const [events, setEvents] = useState<string[]>([]);

  // Fetch agent details when selection changes
  useEffect(() => {
    if (!selectedAgentId) {
      setSelectedAgentDetails(null);
      setAgentMemories([]);
      return;
    }

    const fetchAgentDetails = async () => {
      try {
        // 获取智能体详细信息
        const response = await fetch(`${API_BASE}/agents/${selectedAgentId}`);
        const data = await response.json();
        setSelectedAgentDetails(data);
      } catch (error) {
        console.error('Failed to fetch agent details:', error);
      }
    };

    const fetchMemories = async () => {
      try {
        const response = await fetch(`${API_BASE}/agents/${selectedAgentId}/memories`);
        const data = await response.json();
        setAgentMemories(data.memories || []);
      } catch (error) {
        console.error('Failed to fetch memories:', error);
      }
    };

    fetchAgentDetails();
    fetchMemories();
  }, [selectedAgentId]);

  // Fetch recent events
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch(`${API_BASE}/events?limit=20`);
        const data = await response.json();
        // 翻译事件文本
        const translatedEvents = (data.recent_actions || []).map((event: string) => {
          return event
            .replace(/Tick (\d+):/, '时间片 $1:')
            .replace(/GATHER/g, '采集')
            .replace(/REST/g, '休息')
            .replace(/MOVE/g, '移动')
            .replace(/CRAFT/g, '制作')
            .replace(/BUILD/g, '建造')
            .replace(/COMMUNICATE/g, '交流')
            .replace(/EAT/g, '进食')
            .replace(/DRINK/g, '喝水')
            .replace(/TEACH/g, '教学')
            .replace(/TRADE/g, '交易')
            .replace(/Need food/g, '需要食物')
            .replace(/Need water/g, '需要水')
            .replace(/Need wood/g, '需要木材')
            .replace(/Low energy, need to rest/g, '能量低，需要休息')
            .replace(/\(current: (\d+)\)/g, '(当前: $1)')
            // === 新增翻译 ===
            .replace(/结婚了/g, '举办了婚礼 💒')
            .replace(/怀孕了/g, '怀孕了 🤰')
            .replace(/生下了/g, '生下了 👶')
            .replace(/建造了茅屋/g, '建造了茅屋 🏠')
            .replace(/建造了木屋/g, '建造了木屋 🏠')
            .replace(/建造了水井/g, '建造了水井 ⛲')
            .replace(/复活/g, '复活 ⚡')
            .replace(/死亡/g, '去世 💀');
        });
        setEvents(translatedEvents);
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
    return <div className="loading">加载文明中...</div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🏛️ AI 文明模拟器</h1>
        {worldState && (
          <div className="world-info">
            <span>第 {worldState.day} 天</span>
            <span>时间片 {worldState.tick}</span>
            <span>{worldState.time_of_day.toFixed(1)} 小时</span>
            <span className="weather">{worldState.weather}</span>
          </div>
        )}
      </header>

      <div className="app-content">
        <aside className="sidebar-left">
          <div className="agents-panel">
            <h2>智能体 ({agents.length})</h2>
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
            <h3>最近事件</h3>
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
          agent={selectedAgentDetails}
          memories={agentMemories}
          loading={false}
        />
      </aside>
    </div>
  </div>
);
}

export default App;