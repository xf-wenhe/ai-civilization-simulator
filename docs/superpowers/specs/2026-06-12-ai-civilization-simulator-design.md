# Multi-Agent AI Civilization Simulator

## Overview
An autonomous world where AI agents (powered by Claude) build a civilization from scratch. Each agent has personality, goals, memory, and interacts with others. The civilization emerges through their collective autonomous actions.

## Architecture

### Agent System
- **Agent Identity**: Unique name, personality traits (Big Five model), skills, goals
- **Memory System**: Episodic memory (events), semantic memory (facts about world/others), procedural memory (learned skills)
- **Decision Making**: Perception → Goal evaluation → Action selection → Learning loop
- **Social Graph**: Relationships with other agents (trust, friendship, rivalry)

### World Engine
- **Environment**: Grid-based world with biomes, resources, weather, day/night cycle
- **Resources**: Food, materials, knowledge artifacts, tools
- **Locations**: Settlements, wilderness, resource nodes, landmarks
- **Events**: Natural phenomena, conflicts, discoveries, disasters

### Interaction System
- **Communication**: Natural language dialogue between agents
- **Actions**: Move, gather, craft, trade, teach, build, socialize, rest
- **Coordination**: Agents can form groups, delegate tasks, negotiate

### Economy & Society
- **Resources**: Scarcity-driven economy, storage, trade routes
- **Knowledge**: Skills can be taught, books written, discoveries shared
- **Social Structures**: Emergent families, guilds, governments, religions
- **Culture**: Shared beliefs, traditions, taboos, art, stories

## Technical Stack

### Backend (Python)
- **Agent Orchestrator**: Manages agent instances, scheduling, coordination
- **World State Manager**: Environment simulation, resource tracking, event generation
- **Memory Service**: Persistent agent memories using conversation history + vector store
- **Action Processor**: Validates and executes agent actions, updates world state

### AI Integration
- **Claude API**: Each agent runs on Claude with system prompt defining personality/goals
- **Conversation History**: Last N turns as short-term memory
- **Vector Database**: Long-term semantic memory (ChromaDB or similar)
- **Embedding Storage**: Agent reflections, important events, learned facts

### Frontend (React + TypeScript)
- **World Map**: Real-time visualization of agents, locations, resources
- **Agent View**: Individual agent status, inventory, relationships, memories
- **Event Log**: Chronological stream of actions, conversations, events
- **Analytics**: Civilization metrics (population, resources, social structures)
- **Intervention Panel**: Optional human observer actions

### Storage
- **SQLite**: World state, agent state, locations, resources
- **JSON Files**: Agent memories, conversation logs
- **Vector DB**: Semantic search over agent knowledge

## Key Features

### 1. True Agent Autonomy
Agents act based on their personality, goals, and memories - no scripts or predetermined behaviors. Each runs its own decision loop.

### 2. Sophisticated Memory
- Episodic: "Yesterday I met Alice near the river"
- Semantic: "Bob is a skilled hunter but untrustworthy"
- Procedural: Knowledge of how to craft tools, build shelters

### 3. Emergent Civilization
No hardcoded social structures. Agents form relationships, alliances, hierarchies through natural interaction.

### 4. Observer Experience
Watch civilization evolve in real-time. Analyze patterns. See emergence happen.

### 5. Persistence
World state and agent memories persist across sessions. Civilization continues growing.

### 6. Human Intervention (Optional)
Observer can:
- Introduce new agents with specific personalities
- Trigger events (weather, resource discovery, conflicts)
- Modify world conditions
- Guide agents through suggestions

## Implementation Phases

### Phase 1: Core Agent System
- Agent class with personality, goals, memory
- Claude API integration
- Basic action system (move, gather, communicate)
- Simple world state (grid, resources)

### Phase 2: Memory & Learning
- Episodic memory storage
- Relationship tracking
- Goal prioritization based on needs
- Learning from outcomes

### Phase 3: Social Dynamics
- Communication system
- Trade negotiations
- Knowledge transfer
- Relationship evolution

### Phase 4: World Complexity
- Biomes and weather
- Resource scarcity and regeneration
- Crafting and building
- Locations and territories

### Phase 5: Emergence & Culture
- Group formation
- Social structures
- Shared knowledge
- Cultural artifacts

### Phase 6: Frontend & Visualization
- Real-time map view
- Agent detail panels
- Event stream
- Analytics dashboard

### Phase 7: Polish & Observation
- Performance optimization
- Observer controls
- Export/share capabilities
- Documentation

## Success Criteria
- Agents exhibit emergent, unscripted behaviors
- Civilization develops recognizable social structures
- Observers find the evolution genuinely interesting and unpredictable
- System runs autonomously for extended periods
- Agent decisions make sense given their personalities and memories
