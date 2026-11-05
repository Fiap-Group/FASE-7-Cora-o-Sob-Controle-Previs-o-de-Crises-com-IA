import json
import sys
from collections.abc import Generator
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from fastapi.testclient import TestClient

BACKEND = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND))

from shared.rag_system import Chunk, GenomicChunker, TextCleaner, VectorStore  # noqa: E402
from shared.prompts import DISCLAIMER_RESPOSTA, SYSTEM_PROMPT_RAG  # noqa: E402
from shared.observabilidade import FormatadorJSON, Metricas, hash_pergunta  # noqa: E402
from src.main import app  # noqa: E402
from src.modules.rag.dependencies import (  # noqa: E402
    EstadoIndexacao,
    get_estado,
    get_pipeline,
    get_pipeline_if_exists,
)

RELATORIO_EXEMPLO = BACKEND / "sample_sprint1_output.json"


def chunks_de(paciente: str, n: int) -> list[Chunk]:
    """Gera `n` chunks fictícios com embedding aleatório para um paciente de teste."""
    saida: list[Chunk] = []
    for i in range(n):
        vetor = np.random.rand(8).astype(np.float32)
        vetor /= np.linalg.norm(vetor)
        saida.append(Chunk(
            chunk_id=f"{paciente}-{i}", section="riscos_doencas", subsection=None,
            text=f"Paciente {paciente} risco {i}", metadata={}, embedding=vetor,
        ))
    return saida


def test_reindexar_substitui_o_perfil_anterior():
    """Testa que reindexar substitui os chunks do perfil anterior pelos do novo."""
    vs = VectorStore(use_faiss=False)
    vs.add_chunks(chunks_de("CARLOS", 3))
    vs.reset()
    vs.add_chunks(chunks_de("MARIA", 3))
    assert len(vs.chunks) == 3
    assert {c.text.split()[1] for c in vs.chunks} == {"MARIA"}


def test_busca_depois_do_reset_so_devolve_dados_novos():
    """Testa que a busca depois de um reset só devolve chunks do perfil atual."""
    vs = VectorStore(use_faiss=False)
    vs.add_chunks(chunks_de("CARLOS", 3))
    vs.reset()
    vs.add_chunks(chunks_de("MARIA", 3))
    consulta = np.random.rand(8).astype(np.float32)
    resultados = vs.search(consulta, top_k=5)
    assert resultados
    assert all("MARIA" in r.chunk.text for r in resultados)


class EmbeddingFalso:
    """Embeddings aleatórios de dimensão 8, sem carregar o modelo real."""

    def embed(self, textos: list[str]) -> np.ndarray:
        """Gera embeddings aleatórios normalizados, sem usar nenhum modelo real."""
        vetores = np.random.rand(len(textos), 8).astype(np.float32)
        return vetores / np.linalg.norm(vetores, axis=1, keepdims=True)


def test_index_patient_substitui_o_relatorio_anterior():
    """Testa que indexar um segundo relatório não mantém chunks do primeiro no índice."""
    from shared.rag_system import GenomicRAGPipeline

    dados = json.loads(RELATORIO_EXEMPLO.read_text(encoding="utf-8"))
    segundo = json.loads(json.dumps(dados))
    segundo["paciente"]["nome"] = "Maria Souza"
    segundo["paciente"]["id"] = "PAC-OUTRO"
    segundo["paciente"]["sexo"] = "feminino"

    pipeline = GenomicRAGPipeline(
        cleaner=TextCleaner(),
        chunker=GenomicChunker(TextCleaner()),
        embedding_engine=EmbeddingFalso(),  # type: ignore[arg-type]
        vector_store=VectorStore(use_faiss=False),
        retriever=None,  # type: ignore[arg-type]
        generator=None,  # type: ignore[arg-type]
    )
    n1 = pipeline.index_patient(dados)
    n2 = pipeline.index_patient(segundo)

    assert len(pipeline.vector_store.chunks) == n2
    assert n1 != 0
    textos = " ".join(c.text for c in pipeline.vector_store.chunks)
    assert "Feminino" in textos or "feminino" in textos
    assert "masculino" not in textos.lower()


def test_perfil_enviado_ao_llm_nao_tem_identificadores():
    """Testa que o chunk de perfil não contém identificadores diretos do paciente."""
    dados = json.loads(RELATORIO_EXEMPLO.read_text(encoding="utf-8"))
    chunker = GenomicChunker(TextCleaner())
    chunks = chunker.chunk_json(dados)
    perfil = next(c for c in chunks if c.section == "perfil")

    assert "Carlos" not in perfil.text
    assert "1985-03-15" not in perfil.text
    assert "PAC-2024-001" not in perfil.text
    assert "Sexo" in perfil.text or "sexo" in perfil.text.lower()


def test_log_nao_contem_texto_da_pergunta():
    """Testa que o log de uma pergunta nunca contém o texto original da pergunta."""
    pergunta_secreta = "meu exame mostrou algo grave em CARLOS SILVA"
    registro = __import__("logging").LogRecord(
        name="genera_api", level=20, pathname="", lineno=0,
        msg="Pergunta respondida", args=(), exc_info=None,
    )
    registro.evento = "pergunta"
    registro.pergunta_hash = hash_pergunta(pergunta_secreta)
    registro.pergunta_chars = len(pergunta_secreta)
    linha = FormatadorJSON().format(registro)
    assert pergunta_secreta not in linha
    assert "CARLOS" not in linha
    assert json.loads(linha)["pergunta_chars"] == len(pergunta_secreta)


class PipelineFalso:
    """Substitui o pipeline real nos testes de endpoint (sem modelo nem LLM)."""

    def __init__(self, resposta_grounded: bool = True):
        """Guarda um vector store vazio e a flag de ancoragem usada nas respostas fake."""
        self.vector_store = VectorStore(use_faiss=False)
        self._indexed = True
        self._grounded = resposta_grounded

    def index_patient(self, dados: dict[str, Any]) -> int:
        """Simula a indexação de um perfil, sempre devolvendo 3 chunks."""
        return 3

    def limpar_indice(self):
        """Simula a limpeza do índice do paciente."""
        self.vector_store.reset()
        self._indexed = False

    def answer(self, pergunta: str) -> Any:
        """Devolve uma resposta fake, sem chamar nenhum LLM de verdade."""
        from types import SimpleNamespace
        chunk = SimpleNamespace(section="riscos_doencas", subsection=None, text="trecho")
        return SimpleNamespace(
            answer="Resposta de teste." + DISCLAIMER_RESPOSTA,
            grounded=self._grounded,
            retrieved_chunks=[SimpleNamespace(chunk=chunk, score=0.9)],
        )


@pytest.fixture
def cliente() -> Generator[TestClient, None, None]:
    """Substitui os providers do módulo RAG por doubles de teste."""
    estado_teste = EstadoIndexacao()
    pipeline_falso = PipelineFalso()
    app.dependency_overrides[get_estado] = lambda: estado_teste
    app.dependency_overrides[get_pipeline] = lambda: pipeline_falso
    app.dependency_overrides[get_pipeline_if_exists] = lambda: pipeline_falso
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_health_e_metrics_respondem(cliente: TestClient) -> None:
    """Testa que os endpoints de health e metrics respondem com sucesso."""
    assert cliente.get("/api/health").status_code == 200
    resposta = cliente.get("/api/metrics")
    assert resposta.status_code == 200
    assert "contadores" in resposta.json()


def test_chat_sem_indexacao_retorna_400_com_mensagem_reconhecida_pelo_front(cliente: TestClient) -> None:
    """Testa que o chat sem nenhum perfil indexado devolve 400 com mensagem clara."""
    resposta = cliente.post("/api/chat", json={"question": "oi"})
    assert resposta.status_code == 400
    assert "indexado" in resposta.json()["error"]


def test_index_depois_chat_e_reset(cliente: TestClient) -> None:
    """Testa o fluxo completo de indexar, perguntar no chat e depois resetar o índice."""
    assert cliente.post("/api/index", json={"paciente": {}}).status_code == 200
    resposta = cliente.post("/api/chat", json={"question": "qual meu risco?"})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert "answer" in corpo and "sources" in corpo and "grounded" in corpo
    assert DISCLAIMER_RESPOSTA.strip() in corpo["answer"]

    assert cliente.post("/api/reset").status_code == 200
    assert cliente.post("/api/chat", json={"question": "oi"}).status_code == 400


def test_erro_interno_nao_vaza_detalhe_ao_cliente(cliente: TestClient) -> None:
    """Testa que um erro interno do pipeline não expõe detalhes ao cliente."""
    class PipelineQuebrado(PipelineFalso):
        """Pipeline fake que sempre falha ao responder."""

        def answer(self, pergunta: str) -> Any:
            """Simula uma falha ao gerar a resposta."""
            raise RuntimeError("segredo interno: chave xyz")

    app.dependency_overrides[get_pipeline] = lambda: PipelineQuebrado()
    estado = app.dependency_overrides[get_estado]()
    estado.indexado = True

    resposta = cliente.post("/api/chat", json={"question": "oi"})
    assert resposta.status_code == 500
    assert "segredo interno" not in resposta.text


def test_metricas_calculam_percentis():
    """Testa que as métricas calculam corretamente os percentis de latência."""
    m = Metricas()
    for ms in range(1, 101):
        m.registrar_latencia(float(ms))
    resumo = m.resumo()
    assert resumo["latencia_ms"]["amostras"] == 100
    assert 45 <= resumo["latencia_ms"]["p50"] <= 55
    assert resumo["latencia_ms"]["p95"] >= 90


def test_prompt_pede_respostas_curtas_e_inclui_glossario():
    """Testa que o prompt de sistema pede respostas curtas e inclui o glossário."""
    assert "120 palavras" in SYSTEM_PROMPT_RAG
    assert "GLOSSÁRIO" in SYSTEM_PROMPT_RAG
    assert "haplogrupo" in SYSTEM_PROMPT_RAG
    assert "LIMITES DO AGENTE" in SYSTEM_PROMPT_RAG


def test_disclaimer_e_curto_e_claro():
    """Testa que o disclaimer é curto e deixa claro que não é um diagnóstico."""
    texto = DISCLAIMER_RESPOSTA.strip()
    assert "não um diagnóstico" in texto
    assert len(texto.split()) <= 30
