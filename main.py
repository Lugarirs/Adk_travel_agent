"""
Travel Concierge — FastAPI Backend
Serves the ADK multi-agent pipeline via REST + Server-Sent Events (SSE).
"""

import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv

load_dotenv()  # Must be before ADK/genai imports so GOOGLE_API_KEY is in env

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── ADK imports (after load_dotenv) ───────────────────────────────────────────
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agent import root_agent  # root_agent → FlightAgent, HotelAgent, ActivitiesAgent

# ── Singletons — created once at startup, reused for every request ─────────────
APP_NAME = "travel_concierge"
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"✈️  Travel Concierge starting — root agent: {root_agent.name}")
    print(f"   Sub-agents: FlightAgent, HotelAgent, ActivitiesAgent")
    yield
    print("🛬  Travel Concierge shutting down...")


# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Travel Concierge API",
    description="Multi-agent AI travel planner powered by Google ADK + Gemini",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class SessionResponse(BaseModel):
    session_id: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    agent_name: str


# ── Session helper (async — ADK session methods are all coroutines) ────────────
async def get_or_create_session(session_id: str | None) -> str:
    if not session_id:
        session_id = str(uuid.uuid4())

    existing = await session_service.get_session(
        app_name=APP_NAME, user_id="user", session_id=session_id
    )
    if existing is None:
        await session_service.create_session(
            app_name=APP_NAME, user_id="user", session_id=session_id
        )
    return session_id


# ── Streaming generator ────────────────────────────────────────────────────────
async def run_agent_stream(message: str, session_id: str) -> AsyncGenerator[str, None]:
    """Run the ADK agent pipeline and yield SSE-formatted events."""
    user_message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=message)],
    )

    try:
        async for event in runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=user_message,
        ):
            # Sub-agent status updates
            author = getattr(event, "author", "") or ""
            if author and author != root_agent.name:
                status_map = {
                    "FlightAgent":     "✈️ Searching for flights...",
                    "HotelAgent":      "🏨 Finding hotels...",
                    "ActivitiesAgent": "🗺️ Discovering activities...",
                }
                status = status_map.get(author, f"⚙️ {author} working...")
                yield f"data: {json.dumps({'type': 'status', 'content': status})}\n\n"

            # Final response — stream word by word
            if event.is_final_response() and event.content and event.content.parts:
                for part in event.content.parts:
                    if not part.text:
                        continue
                    words = part.text.split(" ")
                    for i, word in enumerate(words):
                        chunk = word + (" " if i < len(words) - 1 else "")
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk, 'session_id': session_id})}\n\n"
                        await asyncio.sleep(0.02)

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        return

    yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.post("/api/session", response_model=SessionResponse)
async def create_session():
    """Create a new conversation session."""
    session_id = str(uuid.uuid4())
    await session_service.create_session(
        app_name=APP_NAME, user_id="user", session_id=session_id
    )
    return {"session_id": session_id}


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """Stream agent response via Server-Sent Events."""
    session_id = await get_or_create_session(req.session_id)
    return StreamingResponse(
        run_agent_stream(req.message, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Non-streaming chat — waits for the full response."""
    session_id = await get_or_create_session(req.session_id)
    user_message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=req.message)],
    )
    final_response = ""
    async for event in runner.run_async(
        user_id="user",
        session_id=session_id,
        new_message=user_message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text

    if not final_response:
        raise HTTPException(status_code=500, detail="No response from agent")

    return {
        "session_id": session_id,
        "response": final_response,
        "agent_name": root_agent.name,
    }


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "root_agent": root_agent.name,
        "sub_agents": ["FlightAgent", "HotelAgent", "ActivitiesAgent"],
        "model": "gemini-3.1-flash-lite",
    }


# ── Serve frontend (registered LAST — it's a catch-all) ───────────────────────
try:
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
except RuntimeError:
    pass  # static/ not present — API-only mode


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)