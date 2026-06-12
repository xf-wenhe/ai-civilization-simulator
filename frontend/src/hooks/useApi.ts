import { useState, useEffect } from 'react';
import { Agent, WorldState, WorldMap } from '../types';

const API_BASE = 'http://localhost:8888';  // 后端改为8888

export function useWorldState() {
  const [worldState, setWorldState] = useState<WorldState | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWorldState = async () => {
      try {
        const response = await fetch(`${API_BASE}/world`);
        const data = await response.json();
        setWorldState(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch world state:', error);
        setLoading(false);
      }
    };

    fetchWorldState();
    const interval = setInterval(fetchWorldState, 1000);
    return () => clearInterval(interval);
  }, []);

  return { worldState, loading };
}

export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch(`${API_BASE}/agents`);
        const data = await response.json();
        setAgents(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch agents:', error);
        setLoading(false);
      }
    };

    fetchAgents();
    const interval = setInterval(fetchAgents, 1000);
    return () => clearInterval(interval);
  }, []);

  return { agents, loading };
}

export function useWorldMap() {
  const [worldMap, setWorldMap] = useState<WorldMap | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMap = async () => {
      try {
        const response = await fetch(`${API_BASE}/world/map`);
        const data = await response.json();
        setWorldMap(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch world map:', error);
        setLoading(false);
      }
    };

    fetchMap();
    const interval = setInterval(fetchMap, 5000);
    return () => clearInterval(interval);
  }, []);

  return { worldMap, loading };
}

export function useAgentDetails(agentId: string | null) {
  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!agentId) {
      setAgent(null);
      return;
    }

    const fetchAgent = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE}/agents/${agentId}`);
        const data = await response.json();
        setAgent(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch agent details:', error);
        setLoading(false);
      }
    };

    fetchAgent();
  }, [agentId]);

  return { agent, loading };
}