import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from shared.observabilidade import configurar_logs

configurar_logs()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.db import Base, engine

from src.modules.auth.router import router as auth_router
from src.modules.perfil.router import router as perfil_router
from src.modules.rag.router import router as rag_router
from src.modules.risco.mqtt_listener import iniciar_mqtt_listener
from src.modules.risco.router import router as risco_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Cria as tabelas do banco e sobe o listener MQTT junto do boot do servidor."""
    Base.metadata.create_all(engine)
    iniciar_mqtt_listener()
    yield


app = FastAPI(title="CardioIA", lifespan=lifespan)

origens_permitidas = [
    origem.strip()
    for origem in os.getenv(
        "CORS_ORIGINS", "http://localhost:8081,http://localhost:19006,http://localhost:5173"
    ).split(",")
    if origem.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_permitidas,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def tratar_http_exception(_request, exc: HTTPException) -> JSONResponse:
    """Converte o erro para o formato {"error": "..."} esperado pelo front."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


app.include_router(auth_router)
app.include_router(perfil_router)
app.include_router(rag_router)
app.include_router(risco_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        reload=False,
    )
