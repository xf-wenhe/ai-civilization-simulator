export interface Agent {
  id: string;
  name: string;
  position: [number, number];
  health: number;
  energy: number;
  inventory: Record<string, number>;
  current_action: string | null;
  skills?: Record<string, number>;
  personality?: Record<string, number>;
  goals?: Array<{
    description: string;
    priority: number;
    completed: boolean;
  }>;
}

export interface WorldState {
  tick: number;
  day: number;
  time_of_day: number;
  weather: string;
  width: number;
  height: number;
}

export interface Location {
  position: [number, number];
  biome: string;
  resources: Record<string, number>;
  agents_present: string[];
  buildings: string[];
}

export interface WorldMap {
  width: number;
  height: number;
  locations: Record<string, Location>;
}

export interface Memory {
  content: string;
  timestamp: number;
  importance: number;
  memory_type: string;
}

export interface Relationship {
  agent_id: string;
  trust: number;
  friendship: number;
  interactions: number;
}