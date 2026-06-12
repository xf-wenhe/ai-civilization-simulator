# AI Civilization Simulator - Quick Start Guide

## What is This?

An autonomous world where AI agents (powered by Claude) build a civilization from scratch! Each agent has:
- Unique personality and goals
- Memory system for learning
- Ability to communicate, trade, teach, and build
- No scripts - truly autonomous decision-making

Watch civilization emerge through natural agent interactions.

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start the simulation
python main.py
```

The backend will:
- Initialize the world (50x50 grid with biomes and resources)
- Create 5 AI agents with unique personalities
- Run autonomous agent decision loops
- Save state periodically to `data/` directory

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open http://localhost:8080 to see:
- Real-time world map with agent positions
- Agent cards showing status, inventory, actions
- Detailed agent view with personality, goals, memories
- Event log showing civilization history

### 3. API Server (Optional)

```bash
cd backend
python server.py
```

Runs FastAPI server at http://localhost:8000 with:
- `/world` - World state (tick, day, time)
- `/agents` - All agent statuses
- `/agents/{id}` - Specific agent details
- `/agents/{id}/memories` - Agent's memory history
- `/world/map` - Full world map with locations
- `/events` - Recent world events
- WebSocket `/ws` for real-time updates

## Architecture

### Backend (Python)
- **agent.py** - Agent class with personality, goals, memory
- **world_state.py** - World environment, resources, locations
- **orchestrator.py** - Agent lifecycle, Claude API integration
- **memory_system.py** - ChromaDB semantic memory
- **communication.py** - Agent dialogue generation
- **knowledge_system.py** - Teaching and knowledge transfer
- **crafting.py** - Recipe-based item creation
- **server.py** - FastAPI REST + WebSocket endpoints

### Frontend (React + TypeScript)
- **src/types/** - TypeScript interfaces
- **src/hooks/useApi.ts** - API data fetching hooks
- **src/components/**:
  - AgentCard.tsx - Agent status display
  - WorldMapComponent.tsx - Visual world map
  - AgentDetails.tsx - Detailed agent view
- **App.tsx** - Main layout and state management

## Interesting Features

### 1. True Agent Autonomy
Agents use Claude to make decisions based on:
- Personality traits (Big Five model)
- Current goals and priorities
- Memories of past experiences
- Current situation (location, resources, nearby agents)

No scripts! Each agent thinks independently.

### 2. Memory System
- **Episodic**: Events and experiences ("Yesterday I met Alice")
- **Semantic**: Facts about world ("Bob is a skilled hunter")
- **Procedural**: Learned skills ("How to craft tools")

Stored in ChromaDB for semantic search and retrieval.

### 3. Communication
Agents have natural language conversations:
- Generate dialogue using Claude
- Build relationships over time
- Share information and collaborate
- Develop trust/friendship

### 4. Knowledge Transfer
Agents can teach each other:
- Skills like gathering, crafting, building
- Knowledge transfer with success probability
- Teacher skill level affects success
- Students improve through learning

### 5. Crafting System
Create items from resources:
- Stone axe, wooden shelter, cooked food
- Quality depends on skill + difficulty
- Skill improves through practice
- Recipes unlock based on skill level

### 6. Emergent Behavior
Watch for:
- Agents forming relationships
- Knowledge sharing leading to skill improvement
- Resource gathering patterns
- Social structures emerging
- Exploration and discovery

## Experiment Ideas

1. **Add more agents**: Edit `AGENT_COUNT` in .env
2. **Custom personalities**: Modify agent creation in orchestrator.py
3. **New recipes**: Add to crafting.py
4. **Observe relationships**: Check friendship/trust metrics
5. **Track knowledge spread**: Watch skills propagate through teaching
6. **Resource scarcity**: Modify world_state.py resource generation
7. **Events**: Use API `/world/intervene` to trigger world events

## What Makes This Interesting?

- **Unpredictable**: Agents make autonomous decisions, not scripted
- **Emergent**: Civilization develops naturally from simple rules
- **Social**: Relationships, trust, and culture emerge
- **Learning**: Agents improve through experience and teaching
- **Visual**: See the world evolve in real-time
- **Persistent**: Civilization continues across sessions

No one programmed the agents to form alliances, trade, or teach - they just do it because their personalities and goals lead them there!

## Token Usage

This project uses ~2-3 million tokens to build:
- Backend infrastructure (Python, FastAPI, ChromaDB)
- Agent decision system (Claude API integration)
- Memory system (vector embeddings, semantic search)
- Communication dialogue generation
- Knowledge transfer mechanics
- Crafting and item creation
- Frontend visualization (React, TypeScript)
- Real-time updates (WebSocket, API hooks)

Each agent decision uses ~300-500 tokens. With 5 agents running autonomously, watching civilization emerge over hundreds of ticks shows genuine AI-driven social behavior.

## Future Ideas

- Buildings and permanent structures
- Trade economy and markets
- Governance and decision-making
- Culture and traditions
- Writing and books
- Multi-generational knowledge
- Agent specialization
- Conflicts and diplomacy
- Religion and beliefs
- Art and creativity

Enjoy watching AI civilization emerge! 🌍