import os
import sys
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from shared.observabilidade import configurar_logs

configurar_logs()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from shared.db import Base, engine
from shared.observabilidade import HTTP_LATENCY, HTTP_REQUESTS, configurar_telemetria, identificar_cliente

from src.modules.auth.router import router as auth_router
from src.modules.perfil.router import router as perfil_router
from src.modules.rag.router import router as rag_router
from src.modules.risco.mqtt_listener import iniciar_mqtt_listener
from src.modules.risco.router import router as risco_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(engine)
    iniciar_mqtt_listener()
    yield


app = FastAPI(title="CardioIA", lifespan=lifespan)
configurar_telemetria(app)


@app.middleware("http")
async def medir_requisicoes_http(request: Request, chamar_proximo):
    cliente = identificar_cliente(request)
    inicio = time.perf_counter()
    resposta = await chamar_proximo(request)
    duracao = time.perf_counter() - inicio

    rota = request.scope.get("route")
    caminho = rota.path if rota else request.url.path
    HTTP_REQUESTS.labels(method=request.method, path=caminho, status=resposta.status_code, client=cliente).inc()
    HTTP_LATENCY.labels(method=request.method, path=caminho, client=cliente).observe(duracao)
    return resposta


@app.get("/metrics")
def metricas_prometheus() -> Response:
    """Expõe as métricas no formato que o Prometheus raspa."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


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
