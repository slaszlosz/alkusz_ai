from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.db.database import init_db
from app.api import chat, documents, metrics, evaluation

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    await init_db()
    print("Database initialized")
    print("AlkuszAI API v1.0.0 with Evaluation Framework")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="AlkuszAI API",
    description="Vállalati tudásbázis chatbot API with RAG Evaluation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(metrics.router)
app.include_router(evaluation.router)


@app.get("/")
async def root():
    return {
        "message": "AlkuszAI API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
