"""
=============================================================================
API REST · CardioIA — Fase 7 (FastAPI)
=============================================================================
Ponto de entrada da aplicação (equivalente ao app.ts/main.ts do Nest): cria
o app FastAPI, registra os módulos (cada um com seu próprio router/providers
em `src/modules/`) e expõe os endpoints HTTP.

Execução local:
    cp .env.example .env     # preencher GEMINI_API_KEY
    pip install -r requirements.txt
    python -m src.main                         # sobe com uvicorn embutido
    # ou, com reload automático em desenvolvimento:
    uvicorn src.main:app --reload --port 5000

Variáveis de ambiente relevantes:
    HOST          endereço de escuta (padrão 127.0.0.1; Docker usa 0.0.0.0)
    PORT          porta (padrão 5000)
    CORS_ORIGINS  origens do front permitidas, separadas por vírgula
=============================================================================
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # app/backend, p/ achar src/ e shared/

from dotenv import load_dotenv

load_dotenv()

from shared.observabilidade import configurar_logs

configurar_logs()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.modules.rag.router import router as rag_router

app = FastAPI(title="CardioIA")

origens_permitidas = [
    origem.strip()
    for origem in os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:19006").split(",")
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
    """Mantém o mesmo formato de erro que o front já espera: {"error": "..."}
    em vez do {"detail": "..."} padrão do FastAPI."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# Cada módulo novo (preditivo, agentes, ...) entra aqui como um
# app.include_router(...) a mais — igual um import de módulo no AppModule
# do Nest.
app.include_router(rag_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        reload=False,
    )
