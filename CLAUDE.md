# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Civilization Simulator - autonomous AI agents build a civilization through natural interactions using Claude API for decision-making.

## Common Commands

### Backend (Python FastAPI)
```bash
# Start backend server (port 8888)
cd backend
python3 working_server.py

# Or with virtual environment
python3 -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
python working_server.py
```

### Frontend (React + TypeScript + Vite)
```bash
# Start frontend dev server (port 9000)
cd frontend
npm install
npm run dev
```

### Combined Start
```bash
# Start both backend and frontend
./start.sh
```

## Architecture

### Backend Structure (Python)
- **working_server.py** - Production FastAPI server (port 8888)
  - REST endpoints: `/world`, `/world/map`, `/agents`, `/agents/{id}`, `/events`
  - Simulation loop runs every 3 seconds
  - Returns agent data with health, energy, skills, personality fields

- **agent.py** - Agent class with personality (Big Five), goals, skills, inventory
- **world_state.py** - World environment (10x10 grid), biomes, resources
- **orchestrator.py** - Agent lifecycle, decision-making with Claude API
- **memory_system.py** - ChromaDB semantic memory (episodic/semantic/procedural)
- **communication.py** - Natural language dialogue generation
- **knowledge_system.py** - Teaching and knowledge transfer
- **crafting.py** - Recipe-based item creation

Key dependencies: FastAPI, uvicorn, anthropic (Claude API), chromadb, python-dotenv

### Frontend Structure (React + TypeScript)
- **src/App.tsx** - Main application container
  - Fetches agents list, world state, world map
  - Calls `/agents/{id}` for detailed agent info (skills, personality)
  - Translates event descriptions to Chinese

- **src/hooks/useApi.ts** - Data fetching hooks for `/world`, `/agents`, `/world/map`
- **src/components/AgentCard.tsx** - Agent status card with health/energy bars
- **src/components/AgentDetails.tsx** - Detailed view showing personality, skills, memories
- **src/components/WorldMapComponent.tsx** - Visual 10x10 grid map (40px cell size)
- **src/constants.ts** - Chinese labels for personality traits, action/action colors

Key dependencies: React 18, TypeScript, Vite, axios

## Port Configuration

- **Backend**: localhost:8888
- **Frontend**: localhost:9000
- Frontend API calls must use port 8888 (not 8000)

## API Endpoints

### Must Include These Fields
- `/world` - Must return: `tick`, `day`, `time_of_day`, `weather`, `width`, `height`
- `/agents` - Must return: `id`, `name`, `position`, `health`, `energy`, `inventory`, `current_action`
- `/agents/{id}` - Must return above fields + `skills`, `personality`
- `/world/map` - Must return: `width`, `height`, `locations` dict keyed by "x,y"
- `/events` - Returns `recent_actions` array (not `events`)

### Field Types
- `personality` - Dict with keys: openness, conscientiousness, extraversion, agreeableness, neuroticism (values 0-1)
- `skills` - Dict with skill names and levels (values 0-1)
- `position` - Array [x, y] of integers
- `current_action` - String or null ("gather", "rest", "move", "craft", etc.)

## UI Localization

Interface is fully Chinese:
- 事件描述翻译："采集" (gather), "休息" (rest), "需要食物" (need food)
- 性格标签："好奇心" (openness), "自律性" (conscientiousness)
- Agent cards show: 健康值, 能量值

## Common Development Patterns

### When adding new API endpoint
1. Add endpoint in working_server.py
2. Include all required fields matching TypeScript interfaces in frontend/src/types/index.ts
3. Test endpoint with curl before frontend integration
4. Frontend fetches via hooks/useApi.ts or directly in App.tsx

### When modifying agent data
- Both `/agents` list and `/agents/{id}` detail must be updated
- `/agents` returns basic fields (health, energy, position)
- `/agents/{id}` returns full details including skills and personality
- Frontend calls detail endpoint when agent is selected

### Frontend data fetching pattern
- useWorldState(), useAgents(), useWorldMap() hooks poll every 1-5 seconds
- Selected agent details fetched separately via direct fetch in useEffect
- Events fetched and translated to Chinese in App.tsx

## Environment Setup

Backend requires:
```bash
ANTHROPIC_API_KEY=<your-key>  # In .env file
USE_SIMULATION=true           # Force simulation mode (no real Claude calls)
```

For simulation mode (no API calls), set `USE_SIMULATION=true` environment variable.

## Key Files for Understanding System

- **PROJECT_OVERVIEW.md** - Comprehensive architecture and features explanation
- **docs/superpowers/specs/2026-06-12-ai-civilization-simulator-design.md** - Design specification