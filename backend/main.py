import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path so 'backend' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.config import CONFIG
from backend.core.data_loader import DataLoader
from backend.ai.reasoning_engine import OperationsReasoningEngine
from backend.ai.chatbot import AirportChatbot
from backend.routers import filters, overview, queue, security, trends, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load all data into memory
    print("Loading data...")
    data_loader = DataLoader()
    data_loader.load_all()

    reasoning_engine = OperationsReasoningEngine(data_loader)
    chatbot = AirportChatbot(reasoning_engine, CONFIG)

    app.state.config = CONFIG
    app.state.data_loader = data_loader
    app.state.reasoning_engine = reasoning_engine
    app.state.chatbot = chatbot

    print("Data loaded. API ready.")
    yield


app = FastAPI(
    title="BIAL Airport Operations Dashboard API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filters.router)
app.include_router(overview.router)
app.include_router(queue.router)
app.include_router(security.router)
app.include_router(trends.router)
app.include_router(chat.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}
