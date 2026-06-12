"""
FastAPI server for AI civilization simulator.
Provides REST API and WebSocket endpoints for the frontend.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import json

from agent import Agent
from world_state import WorldState
from orchestrator import AgentOrchestrator


app = FastAPI(title="AI Civilization Simulator API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator: Optional[AgentOrchestrator] = None


class AgentInfo(BaseModel):
    id: str
    name: str
    position: tuple[int, int]
    health: float
    energy: float
    inventory: Dict[str, int]
    current_action: Optional[str]


class WorldInfo(BaseModel):
    tick: int
    day: int
    time_of_day: float
    weather: str
    width: int
    height: int


@app.on_event("startup")
async def startup_event():
    """Initialize world and orchestrator on server startup"""
    global orchestrator

    world = WorldState(width=50, height=50)
    world.initialize_world()

    orchestrator = AgentOrchestrator(world, agent_count=5)

    # Start simulation in background
    asyncio.create_task(orchestrator.run_simulation_loop(tick_rate=10))


@app.get("/")
async def root():
    """API root"""
    return {"message": "AI Civilization Simulator API", "status": "running"}


@app.get("/world", response_model=WorldInfo)
async def get_world_state():
    """Get current world state"""
    if not orchestrator:
        return {"error": "World not initialized"}

    return {
        "tick": orchestrator.world.tick,
        "day": orchestrator.world.day,
        "time_of_day": orchestrator.world.time_of_day,
        "weather": orchestrator.world.weather,
        "width": orchestrator.world.width,
        "height": orchestrator.world.height
    }


@app.get("/world/map")
async def get_world_map():
    """Get full world map with locations"""
    if not orchestrator:
        return {"error": "World not initialized"}

    return orchestrator.world.to_dict()


@app.get("/agents", response_model=List[AgentInfo])
async def get_agents():
    """Get all agents"""
    if not orchestrator:
        return []

    agents_data = []
    for agent in orchestrator.agents.values():
        agents_data.append({
            "id": agent.id,
            "name": agent.name,
            "position": agent.position,
            "health": agent.health,
            "energy": agent.energy,
            "inventory": agent.inventory,
            "current_action": agent.current_action.value if agent.current_action else None
        })

    return agents_data


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details"""
    if not orchestrator or agent_id not in orchestrator.agents:
        return {"error": "Agent not found"}

    agent = orchestrator.agents[agent_id]
    return agent.to_dict()


@app.get("/agents/{agent_id}/memories")
async def get_agent_memories(agent_id: str, limit: int = 20):
    """Get agent's recent memories"""
    if not orchestrator or agent_id not in orchestrator.agents:
        return {"error": "Agent not found"}

    agent = orchestrator.agents[agent_id]
    recent_memories = agent.memories[-limit:]

    return {
        "agent_id": agent_id,
        "memories": recent_memories
    }


@app.get("/agents/{agent_id}/relationships")
async def get_agent_relationships(agent_id: str):
    """Get agent's relationships"""
    if not orchestrator or agent_id not in orchestrator.agents:
        return {"error": "Agent not found"}

    agent = orchestrator.agents[agent_id]
    return {
        "agent_id": agent_id,
        "relationships": agent.relationships
    }


@app.post("/agents/{agent_id}/goals")
async def add_agent_goal(agent_id: str, goal_description: str, priority: float = 0.5):
    """Add a new goal to an agent"""
    if not orchestrator or agent_id not in orchestrator.agents:
        return {"error": "Agent not found"}

    agent = orchestrator.agents[agent_id]
    from agent import Goal

    agent.goals.append(Goal(description=goal_description, priority=priority))

    return {"status": "success", "goal": goal_description}


@app.get("/events")
async def get_recent_events(limit: int = 50):
    """Get recent world events"""
    if not orchestrator:
        return {"events": []}

    events = orchestrator.world.events_log[-limit:]
    return {
        "tick": orchestrator.world.tick,
        "events": events
    }


@app.post("/world/intervene")
async def intervene_world(event_type: str, description: str):
    """Trigger a world event"""
    if not orchestrator:
        return {"error": "World not initialized"}

    orchestrator.world.events_log.append(f"Tick {orchestrator.world.tick}: INTERVENTION - {event_type}: {description}")

    return {
        "status": "success",
        "event": f"{event_type}: {description}",
        "tick": orchestrator.world.tick
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()

    try:
        while True:
            if orchestrator:
                # Send world state update
                data = {
                    "type": "world_update",
                    "tick": orchestrator.world.tick,
                    "day": orchestrator.world.day,
                    "agents": [
                        {
                            "id": agent.id,
                            "name": agent.name,
                            "position": agent.position,
                            "current_action": agent.current_action.value if agent.current_action else None,
                            "energy": agent.energy
                        }
                        for agent in orchestrator.agents.values()
                    ]
                }
                await websocket.send_json(data)

            await asyncio.sleep(1)  # Update every second

    except WebSocketDisconnect:
        print("WebSocket client disconnected")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)