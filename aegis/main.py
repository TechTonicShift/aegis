import os
from typing import Optional
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aegis.core.config import Settings
from aegis.brain.gateway_engine import GatewayEngine
from aegis.controller.router import create_router

def create_app(settings: Optional[Settings] = None) -> FastAPI:
    if settings is None:
        settings = Settings(
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.88")),
            embedder_type=os.getenv("EMBEDDER_TYPE", "gemini" if os.getenv("GEMINI_API_KEY") else "fast_local"),
        )

    gateway = GatewayEngine(settings)

    app = FastAPI(
        title="Aegis AI Gateway",
        description="High-Throughput Reverse Proxy with Semantic Vector Caching & Multi-Model Failover",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Attach gateway engine to app state for testing and extension
    app.state.gateway = gateway
    app.include_router(create_router(gateway))

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("aegis.main:app", host="0.0.0.0", port=port, reload=True)
