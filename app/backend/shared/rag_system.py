"""
=============================================================================
Sistema RAG Genômico - Challenge Dasa/Genera | Sprint 2
=============================================================================
Engrenagem de Inteligência: Recuperação e Geração de Respostas Contextualizadas
a partir de dados genômicos estruturados.

Arquitetura:
  Sprint 1 JSON → Limpeza → Chunking → Embeddings → VectorStore → Retrieval → LLM

Autor: AI Engineering Team
Versão: 1.0.0
=============================================================================
"""

from __future__ import annotations

import json
import logging
import importlib.util
import re
import time
import unicodedata
from dataclasses import dataclass, field
from typing import Any, cast

import numpy as np

from shared.prompts import DISCLAIMER_RESPOSTA, SYSTEM_PROMPT_RAG

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("rag_genomics")

# Campos do bloco "paciente" que identificam diretamente a pessoa. Ficam fora
# do texto enviado ao LLM (ver GenomicChunker._chunk_patient_profile).
CAMPOS_IDENTIFICADORES = {"id", "nome", "data_nascimento", "cpf", "rg", "telefone", "email", "endereco"}


# ===========================================================================
# 1. MODELOS DE DADOS
# ===========================================================================

@dataclass
class Chunk:
    """Unidade atômica de conhecimento extraída do JSON genômico."""
    chunk_id: str
    section: str          # Ex: "ancestralidade", "risco_doenca", "bem_estar"
    subsection: str | None  # Ex: "europeu", "diabetes_tipo2", "vitamina_d"
    text: str             # Texto limpo e normalizado
    metadata: dict[str, Any]  # Dados originais para referência
    embedding: np.ndarray | None = field(default=None, repr=False)


@dataclass
class RetrievedChunk:
    """Chunk recuperado com seu score de similaridade."""
    chunk: Chunk
    score: float


@dataclass
class RAGResponse:
    """Resposta final gerada pelo sistema RAG."""
    question: str
    answer: str
    retrieved_chunks: list[RetrievedChunk]
    context_used: str
    grounded: bool  # True se a resposta está ancorada no contexto


# ===========================================================================
# 2. LIMPEZA E NORMALIZAÇÃO
# ===========================================================================

class TextCleaner:
    """
    Responsável pela limpeza e normalização de textos genômicos.

    Lida com:
    - Nomenclaturas científicas (rs IDs, genes, variantes)
    - Símbolos especiais médicos
    - Percentuais e valores numéricos
    - Unicode e caracteres especiais
    """

    # Padrões que devem ser preservados intactos
    _PRESERVE_PATTERNS = [
        r'rs\d+',               # SNP IDs (ex: rs429358)
        r'[A-Z][a-z]+\d[A-Z]',  # Variantes proteicas (ex: Arg158Cys)
        r'\d+%',                 # Percentuais
        r'\d+[.,]\d+[xX]',      # Multiplicadores de risco (ex: 1.8x)
    ]

    def __init__(self):
        # Compila regex de preservação
        combined = '|'.join(f'({p})' for p in self._PRESERVE_PATTERNS)
        self._preserve_re = re.compile(combined)

    def clean(self, text: str) -> str:
        """
        Pipeline de limpeza completo.

        Args:
            text: Texto bruto extraído do JSON genômico.

        Returns:
            Texto limpo, normalizado e pronto para embedding.
        """
        if not text:
            return ""

        # 1. Normalização Unicode (mantém acentos do português)
        text = unicodedata.normalize("NFC", text)

        # 2. Remove caracteres de controle (exceto \n e \t)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        # 3. Normaliza espaços e quebras de linha
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]{2,}', ' ', text)

        # 4. Normaliza pontuação genômica comum
        text = text.replace('–', '-').replace('—', '-')
        text = text.replace('"', '"').replace('"', '"')

        # 5. Padroniza separadores de lista
        text = re.sub(r'^\s*[•·▪▸]\s*', '- ', text, flags=re.MULTILINE)

        # 6. Trim final
        text = text.strip()

        return text

    def normalize_genetic_terms(self, text: str) -> str:
        """
        Padroniza terminologia genética para consistência nos embeddings.

        Ex: "Alelo de risco" → "alelo_risco", preservando contexto.
        """
        replacements = {
            r'\bSNP\b': 'variante genética',
            r'\bVUS\b': 'variante de significado incerto',
            r'\bLD\b': 'desequilíbrio de ligação',
            r'\bGWAS\b': 'estudo de associação genômica ampla',
            r'\bPRS\b': 'escore de risco poligênico',
            r'\bOR\b(?=\s+\d)': 'odds ratio',  # Só substitui antes de números
        }
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def clean_and_normalize(self, text: str) -> str:
        """Aplica limpeza + normalização genética em sequência."""
        return self.normalize_genetic_terms(self.clean(text))


# ===========================================================================
# 3. CHUNKING ESTRATÉGICO
# ===========================================================================

class GenomicChunker:
    """
    Divide o JSON genômico em chunks lógicos e semanticamente coesos.

    Estratégia: Chunking por domínio semântico, respeitando a estrutura
    hierárquica do relatório genético (ancestralidade → riscos → bem-estar).
    Cada chunk carrega contexto suficiente para ser compreendido de forma
    independente.
    """

    def __init__(self, cleaner: TextCleaner):
        self.cleaner = cleaner

    def chunk_json(self, genomic_json: dict[str, Any]) -> list[Chunk]:
        """
        Ponto de entrada principal: transforma o JSON em lista de Chunks.

        Args:
            genomic_json: Dicionário com os dados genômicos da Sprint 1.

        Returns:
            Lista de Chunks prontos para embedding.
        """
        chunks: list[Chunk] = []
        patient_id = genomic_json.get("paciente", {}).get("id", "unknown")

        # --- Chunk 1: Perfil do Paciente ---
        chunks.extend(self._chunk_patient_profile(genomic_json, patient_id))

        # --- Chunk 2: Ancestralidade ---
        if "ancestralidade" in genomic_json:
            chunks.extend(
                self._chunk_ancestry(genomic_json["ancestralidade"], patient_id)
            )

        # --- Chunk 3: Riscos de Doenças ---
        if "riscos_doencas" in genomic_json:
            chunks.extend(
                self._chunk_disease_risks(genomic_json["riscos_doencas"], patient_id)
            )

        # --- Chunk 4: Bem-Estar e Farmacogenômica ---
        if "bem_estar" in genomic_json:
            chunks.extend(
                self._chunk_wellness(genomic_json["bem_estar"], patient_id)
            )

        # --- Chunk 5: Recomendações Consolidadas ---
        if "recomendacoes" in genomic_json:
            chunks.extend(
                self._chunk_recommendations(genomic_json["recomendacoes"], patient_id)
            )

        logger.info(f"Chunking concluído: {len(chunks)} chunks gerados para paciente {patient_id}")
        return chunks

    def _make_chunk_id(self, patient_id: str, section: str, index: int) -> str:
        return f"{patient_id}_{section}_{index:03d}"

    def _chunk_patient_profile(self, data: dict[str, Any], patient_id: str) -> list[Chunk]:
        """Extrai perfil básico do paciente como chunk de contexto global."""
        patient = data.get("paciente", {})
        if not patient:
            return []

        # Pseudonimização (LGPD, minimização): identificadores diretos não vão
        # para o texto enviado ao LLM. Os metadados completos continuam no
        # chunk, mas não são usados na geração.
        parts = ["Perfil do paciente:"]
        for key, val in patient.items():
            if key.lower() in CAMPOS_IDENTIFICADORES:
                continue
            label = key.replace("_", " ").capitalize()
            parts.append(f"{label}: {val}")

        text = self.cleaner.clean_and_normalize("\n".join(parts))
        return [Chunk(
            chunk_id=self._make_chunk_id(patient_id, "perfil", 0),
            section="perfil",
            subsection="dados_basicos",
            text=text,
            metadata=patient,
        )]

    def _chunk_ancestry(self, ancestry_data: Any, patient_id: str) -> list[Chunk]:
        """
        Cria chunks de ancestralidade.
        Cada origem geográfica vira um chunk independente para buscas precisas.
        """
        chunks: list[Chunk] = []

        items: list[Any]
        if isinstance(ancestry_data, list):
            items = cast(list[Any], ancestry_data)
        elif isinstance(ancestry_data, dict):
            items = cast(list[Any], cast(dict[str, Any], ancestry_data).get("composicao", [ancestry_data]))
        else:
            return []

        for i, item in enumerate(items):
            origin = item.get("origem", item.get("populacao", f"origem_{i}"))
            pct = item.get("percentual", item.get("porcentagem", "N/A"))
            haplogroup = item.get("haplogrupo", "")
            markers = item.get("marcadores_associados", [])

            parts = [
                f"Ancestralidade {origin}: {pct}% de composição genética.",
            ]
            if haplogroup:
                parts.append(f"Haplogrupo: {haplogroup}.")
            if markers:
                parts.append(f"Marcadores genéticos associados: {', '.join(str(m) for m in markers)}.")

            # Adiciona implicações clínicas se existirem
            if "implicacoes" in item:
                parts.append(f"Implicações clínicas: {item['implicacoes']}.")

            text = self.cleaner.clean_and_normalize(" ".join(parts))
            chunks.append(Chunk(
                chunk_id=self._make_chunk_id(patient_id, "ancestralidade", i),
                section="ancestralidade",
                subsection=str(origin).lower().replace(" ", "_"),
                text=text,
                metadata=item,
            ))

        return chunks

    def _chunk_disease_risks(self, risks_data: Any, patient_id: str) -> list[Chunk]:
        """
        Cada doença vira um chunk rico com risco, variantes e contexto.

        Estratégia: Um chunk por doença para garantir recuperação precisa
        em perguntas como "Qual meu risco de diabetes?".
        """
        chunks: list[Chunk] = []

        items: list[Any]
        if isinstance(risks_data, dict):
            riscos = cast(dict[str, Any], risks_data)
            items = cast(list[Any], riscos.get("doencas", list(riscos.values())))
        elif isinstance(risks_data, list):
            items = cast(list[Any], risks_data)
        else:
            return []

        for i, disease in enumerate(items):
            if not isinstance(disease, dict):
                continue
            disease_d: dict[str, Any] = cast(dict[str, Any], disease)

            name = disease_d.get("nome", disease_d.get("doenca", f"doenca_{i}"))
            risk_level = disease_d.get("nivel_risco", disease_d.get("risco", "N/A"))
            risk_pct = disease_d.get("percentual_risco", "")
            population_pct = disease_d.get("media_populacional", "")
            variants = disease_d.get("variantes", disease_d.get("snps", []))
            genes = disease_d.get("genes", [])
            description = disease_d.get("descricao", "")
            lifestyle = disease_d.get("fatores_estilo_vida", [])

            parts = [f"Risco genético para {name}:"]
            parts.append(f"Nível de risco: {risk_level}.")

            if risk_pct:
                parts.append(f"Risco individual: {risk_pct}%.")
            if population_pct:
                parts.append(f"Média populacional: {population_pct}%.")
            if variants:
                var_str = ', '.join(str(v) for v in variants)
                parts.append(f"Variantes identificadas: {var_str}.")
            if genes:
                parts.append(f"Genes envolvidos: {', '.join(str(g) for g in genes)}.")
            if description:
                parts.append(f"Contexto clínico: {description}")
            if lifestyle:
                lf_str = '; '.join(str(l) for l in lifestyle)
                parts.append(f"Fatores de estilo de vida relevantes: {lf_str}.")

            text = self.cleaner.clean_and_normalize(" ".join(parts))
            chunks.append(Chunk(
                chunk_id=self._make_chunk_id(patient_id, "risco_doenca", i),
                section="riscos_doencas",
                subsection=str(name).lower().replace(" ", "_"),
                text=text,
                metadata=disease_d,
            ))

        return chunks

    def _chunk_wellness(self, wellness_data: dict[str, Any], patient_id: str) -> list[Chunk]:
        """
        Processa dados de bem-estar, nutrição e farmacogenômica.
        Agrupa por subcategoria para manter coesão semântica.
        """
        chunks: list[Chunk] = []
        idx = 0

        for category, items in wellness_data.items():
            if not items:
                continue

            item_list: list[Any] = cast(list[Any], items) if isinstance(items, list) else [items]

            for item in item_list:
                if not isinstance(item, dict):
                    continue
                item_dict: dict[str, Any] = cast(dict[str, Any], item)

                trait = item_dict.get("caracteristica", item_dict.get("nome", item_dict.get("trait", category)))
                result = item_dict.get("resultado", item_dict.get("status", item_dict.get("genotipo", "N/A")))
                impact = item_dict.get("impacto", item_dict.get("descricao", ""))
                recommendation = item_dict.get("recomendacao", "")
                variants = item_dict.get("variantes", [])

                parts = [f"Bem-estar genômico – {category}: {trait}."]
                parts.append(f"Resultado genético: {result}.")

                if impact:
                    parts.append(f"Impacto: {impact}")
                if variants:
                    parts.append(f"Variantes: {', '.join(str(v) for v in variants)}.")
                if recommendation:
                    parts.append(f"Recomendação personalizada: {recommendation}")

                text = self.cleaner.clean_and_normalize(" ".join(parts))
                chunks.append(Chunk(
                    chunk_id=self._make_chunk_id(patient_id, "bem_estar", idx),
                    section="bem_estar",
                    subsection=str(category).lower().replace(" ", "_"),
                    text=text,
                    metadata=item_dict,
                ))
                idx += 1

        return chunks

    def _chunk_recommendations(self, recs_data: Any, patient_id: str) -> list[Chunk]:
        """Consolida recomendações clínicas em chunks acionáveis."""
        chunks: list[Chunk] = []

        items: list[tuple[str, Any]]
        if isinstance(recs_data, dict):
            recs = cast(dict[str, Any], recs_data)
            items = [(k, v) for k, v in recs.items()]
        elif isinstance(recs_data, list):
            itens_lista = cast(list[Any], recs_data)
            items = [(f"recomendacao_{i}", r) for i, r in enumerate(itens_lista)]
        else:
            return []

        for i, (key, rec) in enumerate(items):
            if isinstance(rec, dict):
                rec_dict: dict[str, Any] = cast(dict[str, Any], rec)
                category = rec_dict.get("categoria", key)
                action = rec_dict.get("acao", rec_dict.get("descricao", str(rec_dict)))
                priority = rec_dict.get("prioridade", "")
                specialist = rec_dict.get("especialista", "")

                parts = [f"Recomendação clínica – {category}: {action}"]
                if priority:
                    parts.append(f"Prioridade: {priority}.")
                if specialist:
                    parts.append(f"Especialista indicado: {specialist}.")
            else:
                parts = [f"Recomendação: {str(rec)}"]

            text = self.cleaner.clean_and_normalize(" ".join(parts))
            chunks.append(Chunk(
                chunk_id=self._make_chunk_id(patient_id, "recomendacao", i),
                section="recomendacoes",
                subsection=str(key).lower(),
                text=text,
                metadata={"key": key, "content": rec},
            ))

        return chunks


# ===========================================================================
# 4. EMBEDDINGS
# ===========================================================================

class EmbeddingEngine:
    """
    Gerencia a geração de embeddings vetoriais.

    Suporta dois backends:
    - 'sentence_transformers': Local, gratuito, ideal para desenvolvimento
    - 'openai': API OpenAI, ideal para produção

    A interface é idêntica em ambos os casos (duck typing).
    """

    def __init__(self, backend: str = "sentence_transformers", model_name: str | None = None):
        """
        Args:
            backend: 'sentence_transformers' ou 'openai'
            model_name: Nome do modelo. Se None, usa o padrão do backend.
        """
        self.backend = backend
        self._model: Any = None

        if backend == "sentence_transformers":
            self.model_name = model_name or "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
            self._init_sentence_transformers()
        elif backend == "openai":
            self.model_name = model_name or "text-embedding-3-small"
            self._init_openai()
        else:
            raise ValueError(f"Backend '{backend}' não suportado. Use 'sentence_transformers' ou 'openai'.")

    def _init_sentence_transformers(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Carregando modelo SentenceTransformer: {self.model_name}")
            # CPU é suficiente para o volume de chunks deste projeto e evita
            # falhas de compatibilidade CUDA em máquinas sem GPU configurada.
            self._model = SentenceTransformer(self.model_name, device="cpu")
            logger.info("Modelo carregado com sucesso.")
        except ImportError:
            raise ImportError(
                "Instale o pacote: pip install sentence-transformers\n"
                "Modelo recomendado para PT-BR: paraphrase-multilingual-mpnet-base-v2"
            )

    def _init_openai(self):
        try:
            from openai import OpenAI
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Variável de ambiente OPENAI_API_KEY não definida.")
            self._model = OpenAI(api_key=api_key)
            logger.info(f"Cliente OpenAI inicializado. Modelo: {self.model_name}")
        except ImportError:
            raise ImportError("Instale o pacote: pip install openai")

    def embed(self, texts: list[str]) -> np.ndarray:
        """
        Gera embeddings para uma lista de textos.

        Args:
            texts: Lista de strings para embedar.

        Returns:
            Array numpy de shape (n_texts, embedding_dim).
        """
        if not texts:
            return np.array([])

        if self.backend == "sentence_transformers":
            return self._embed_sentence_transformers(texts)
        elif self.backend == "openai":
            return self._embed_openai(texts)
        raise ValueError(f"Backend de embeddings desconhecido: {self.backend}")

    def _embed_sentence_transformers(self, texts: list[str]) -> np.ndarray:
        embeddings = self._model.encode(
            texts,
            batch_size=32,
            show_progress_bar=len(texts) > 10,
            normalize_embeddings=True,  # L2-normalizado para cosine similarity via dot product
        )
        return np.array(embeddings, dtype=np.float32)

    def _embed_openai(self, texts: list[str]) -> np.ndarray:
        """Gera embeddings via OpenAI API com batching automático."""
        BATCH_SIZE = 100  # Limite da API OpenAI
        all_embeddings: list[Any] = []

        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i + BATCH_SIZE]
            response = self._model.embeddings.create(
                input=batch,
                model=self.model_name,
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        arr = np.array(all_embeddings, dtype=np.float32)
        # Normaliza para cosine similarity via dot product
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        return arr / np.maximum(norms, 1e-10)


# ===========================================================================
# 5. BASE VETORIAL (VECTOR STORE)
# ===========================================================================

class VectorStore:
    """
    Base vetorial em memória com busca por similaridade de cosseno.

    Implementação: FAISS (se disponível) com fallback para NumPy puro.
    Ambos produzem resultados idênticos; FAISS é significativamente mais
    rápido para coleções grandes (>10k chunks).

    Em produção, substituir por ChromaDB, Pinecone ou Weaviate para
    persistência e escalabilidade.
    """

    def __init__(self, embedding_dim: int | None = None, use_faiss: bool = True):
        self.embedding_dim = embedding_dim
        self.chunks: list[Chunk] = []
        self._index: Any = None  # FAISS index
        self._use_faiss = use_faiss and self._faiss_available()

        if self._use_faiss:
            logger.info("VectorStore inicializado com backend FAISS.")
        else:
            logger.info("VectorStore inicializado com backend NumPy (fallback).")

    @staticmethod
    def _faiss_available() -> bool:
        if importlib.util.find_spec("faiss") is not None:
            return True
        logger.warning("FAISS não disponível. Usando NumPy para busca vetorial.")
        return False

    def reset(self):
        """Esvazia o índice. Usado antes de indexar um novo perfil, para que
        dados de um relatório antigo não se misturem com o atual."""
        self.chunks = []
        self._index: Any = None

    def add_chunks(self, chunks: list[Chunk]):
        """
        Adiciona chunks com embeddings ao índice vetorial.

        Args:
            chunks: Lista de Chunks com campo `embedding` preenchido.
        """
        valid = [c for c in chunks if c.embedding is not None]
        if not valid:
            logger.warning("Nenhum chunk com embedding para adicionar.")
            return

        self.chunks.extend(valid)

        if self._use_faiss:
            self._add_faiss(valid)
        # Para NumPy, os embeddings ficam nos próprios Chunks

        logger.info(f"VectorStore: {len(valid)} chunks adicionados. Total: {len(self.chunks)}")

    def _add_faiss(self, chunks: list[Chunk]):
        import faiss
        # Chunks chegam aqui já filtrados (valid), então o embedding nunca é None.
        vectors = np.vstack(cast(list[np.ndarray], [c.embedding for c in chunks])).astype(np.float32)

        if self._index is None:
            dim = vectors.shape[1]
            # IndexFlatIP = Inner Product (equivale a cosine com vetores normalizados)
            self._index = faiss.IndexFlatIP(dim)

        self._index.add(vectors)

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[RetrievedChunk]:
        """
        Busca os top_k chunks mais similares ao embedding da query.

        Args:
            query_embedding: Vetor da pergunta do usuário (1D ou 2D).
            top_k: Número de resultados a retornar.

        Returns:
            Lista de RetrievedChunk ordenada por score decrescente.
        """
        if not self.chunks:
            logger.warning("VectorStore vazio. Nenhum chunk para buscar.")
            return []

        query = np.array(query_embedding, dtype=np.float32)
        if query.ndim == 1:
            query = query.reshape(1, -1)

        # Normaliza query (garante cosine similarity)
        norm = np.linalg.norm(query)
        if norm > 1e-10:
            query = query / norm

        if self._use_faiss:
            return self._search_faiss(query, top_k)
        else:
            return self._search_numpy(query, top_k)

    def _search_faiss(self, query: np.ndarray, top_k: int) -> list[RetrievedChunk]:
        k = min(top_k, len(self.chunks))
        scores, indices = self._index.search(query, k)

        results: list[RetrievedChunk] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:  # FAISS retorna -1 para slots inválidos
                results.append(RetrievedChunk(
                    chunk=self.chunks[int(idx)],
                    score=float(score),
                ))
        return results

    def _search_numpy(self, query: np.ndarray, top_k: int) -> list[RetrievedChunk]:
        """Busca por produto interno (= cosine com vetores L2-normalizados)."""
        # Todo chunk guardado no modo NumPy recebe embedding ao ser adicionado.
        matrix = np.vstack(cast(list[np.ndarray], [c.embedding for c in self.chunks])).astype(np.float32)
        scores = (matrix @ query.T).flatten()

        top_indices = np.argsort(scores)[::-1][:top_k]

        return [
            RetrievedChunk(chunk=self.chunks[int(i)], score=float(scores[i]))
            for i in top_indices
        ]


# ===========================================================================
# 6. RECUPERAÇÃO (RETRIEVAL)
# ===========================================================================

class Retriever:
    """
    Orquestra a recuperação de chunks relevantes para uma pergunta.

    Implementa:
    - Busca por similaridade vetorial
    - Filtragem por score mínimo (evita contexto irrelevante)
    - Deduplicação de seções
    - Montagem do contexto formatado para o LLM
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_engine: EmbeddingEngine,
        top_k: int = 5,
        min_score: float = 0.25,
    ):
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine
        self.top_k = top_k
        self.min_score = min_score

    def retrieve(self, question: str) -> list[RetrievedChunk]:
        """
        Recupera os chunks mais relevantes para a pergunta.

        Args:
            question: Pergunta do paciente em linguagem natural.

        Returns:
            Lista de RetrievedChunk filtrada e ordenada por relevância.
        """
        logger.info(f"Retrieval para: '{question[:80]}...'")

        # Gera embedding da query
        query_embedding = self.embedding_engine.embed([question])[0]

        # Busca vetorial
        results = self.vector_store.search(query_embedding, top_k=self.top_k)

        # Filtra por score mínimo
        filtered = [r for r in results if r.score >= self.min_score]

        if not filtered:
            logger.warning(f"Nenhum chunk acima do score mínimo {self.min_score}. "
                          f"Usando top-1 como fallback.")
            filtered = results[:1] if results else []

        logger.info(f"Chunks recuperados: {len(filtered)} "
                   f"(scores: {[f'{r.score:.3f}' for r in filtered]})")

        return filtered

    def build_context(self, retrieved: list[RetrievedChunk]) -> str:
        """
        Monta o contexto estruturado para injeção no prompt do LLM.

        Formato projetado para minimizar alucinações:
        cada chunk é delimitado e identificado por seção.
        """
        if not retrieved:
            return "Nenhuma informação relevante encontrada no perfil genômico."

        context_parts = ["=== CONTEXTO DO PERFIL GENÔMICO DO PACIENTE ===\n"]

        for i, item in enumerate(retrieved, 1):
            chunk = item.chunk
            context_parts.append(
                f"[Trecho {i} | Seção: {chunk.section} | Relevância: {item.score:.2f}]\n"
                f"{chunk.text}\n"
            )

        context_parts.append("=== FIM DO CONTEXTO ===")
        return "\n".join(context_parts)


# ===========================================================================
# 7. GERAÇÃO (GENERATION)
# ===========================================================================

class LLMGenerator:
    """
    Responsável pela geração de respostas via LLM.

    Design anti-alucinação:
    - Prompt de sistema que instrui o modelo a responder APENAS com base
      no contexto fornecido.
    - Instruções explícitas para admitir incerteza quando informação ausente.
    - Temperatura baixa para respostas factuais e consistentes.
    - Suporta OpenAI, Anthropic (Claude) e Google (Gemini).
    """

    # Definido em prompts.py — mantido separado da lógica do pipeline.
    SYSTEM_PROMPT = SYSTEM_PROMPT_RAG

    def __init__(self, backend: str = "openai", model_name: str | None = None, temperature: float = 0.1):
        """
        Args:
            backend: 'openai', 'anthropic' ou 'gemini'
            model_name: Nome do modelo LLM.
            temperature: Temperatura para geração (baixa = mais factual).
        """
        self.backend = backend
        self.temperature = temperature
        self._client: Any = None

        if backend == "openai":
            self.model_name = model_name or "gpt-4o-mini"
            self._init_openai()
        elif backend == "anthropic":
            self.model_name = model_name or "claude-sonnet-4-20250514"
            self._init_anthropic()
        elif backend == "gemini":
            self.model_name = model_name or "gemini-3.6-flash"
            self._init_gemini()
        else:
            raise ValueError(f"Backend '{backend}' não suportado.")

    def _init_openai(self):
        try:
            from openai import OpenAI
            import os
            self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("pip install openai")

    def _init_anthropic(self):
        try:
            import anthropic
            import os
            self._client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        except ImportError:
            raise ImportError("pip install anthropic")

    def _init_gemini(self):
        try:
            from google import genai
            import os
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Variável de ambiente GEMINI_API_KEY (ou GOOGLE_API_KEY) não definida.")
            self._client = genai.Client(api_key=api_key)
        except ImportError:
            raise ImportError("pip install google-genai")

    def generate(self, question: str, context: str) -> str:
        """
        Gera resposta combinando contexto recuperado + pergunta do usuário.

        Args:
            question: Pergunta original do paciente.
            context: Contexto montado pelo Retriever.

        Returns:
            Resposta gerada pelo LLM.
        """
        user_message = f"{context}\n\nPERGUNTA DO PACIENTE: {question}"

        max_tentativas = 3
        ultimo_erro = None
        for tentativa in range(max_tentativas):
            try:
                if self.backend == "openai":
                    return self._generate_openai(user_message)
                elif self.backend == "anthropic":
                    return self._generate_anthropic(user_message)
                elif self.backend == "gemini":
                    return self._generate_gemini(user_message)
            except Exception as erro:
                ultimo_erro = erro

                # Cota diária/mensal esgotada: não adianta tentar de nova em
                # 1-2s (o provedor pede pra esperar dezenas de segundos ou
                # até o próximo período), então falha rápido com uma
                # mensagem clara em vez de insistir à toa.
                if self._erro_e_cota_esgotada(erro):
                    raise RuntimeError(
                        "O limite gratuito de uso do modelo de IA foi atingido por hoje. "
                        "Tente novamente amanhã, quando a cota diária for renovada."
                    ) from erro

                if not self._erro_e_transitorio(erro) or tentativa == max_tentativas - 1:
                    raise
                espera = 2 ** tentativa  # 1s, 2s
                logger.warning(
                    f"Erro transitório do LLM ({erro}). Tentando de novo em {espera}s "
                    f"(tentativa {tentativa + 1}/{max_tentativas})..."
                )
                time.sleep(espera)

        raise ValueError(f"Backend de LLM desconhecido: {self.backend}") from ultimo_erro

    @staticmethod
    def _erro_e_cota_esgotada(erro: Exception) -> bool:
        """Cota diária/mensal do provedor esgotada — retry curto não resolve."""
        texto = str(erro).lower()
        return "resource_exhausted" in texto or "quota" in texto

    @staticmethod
    def _erro_e_transitorio(erro: Exception) -> bool:
        """Sobrecarga passageira do provedor — vale tentar de novo em segundos."""
        texto = str(erro).lower()
        return any(marcador in texto for marcador in ("503", "unavailable", "overloaded"))

    def _generate_openai(self, user_message: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=self.temperature,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()

    def _generate_anthropic(self, user_message: str) -> str:
        response = self._client.messages.create(
            model=self.model_name,
            max_tokens=600,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            temperature=self.temperature,
        )
        return response.content[0].text.strip()

    def _generate_gemini(self, user_message: str) -> str:
        from google.genai import types

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM_PROMPT,
                temperature=self.temperature,
                # max_output_tokens precisa de folga porque o modelo consome
                # parte do budget em "thinking" interno antes do texto final;
                # sem essa folga (ou com thinking_budget=0, rejeitado por
                # este modelo) a resposta saía cortada no meio.
                max_output_tokens=2048,
                thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW),
            ),
        )
        return response.text.strip()


# ===========================================================================
# 8. PIPELINE RAG COMPLETO
# ===========================================================================

class GenomicRAGPipeline:
    """
    Pipeline RAG completo para o sistema genômico Dasa/Genera.

    Orquestra todos os componentes:
    TextCleaner → GenomicChunker → EmbeddingEngine →
    VectorStore → Retriever → LLMGenerator

    Uso:
        pipeline = GenomicRAGPipeline.from_config(config)
        pipeline.index_patient(genomic_json)
        response = pipeline.answer("Qual meu risco de desenvolver diabetes?")
    """

    def __init__(
        self,
        cleaner: TextCleaner,
        chunker: GenomicChunker,
        embedding_engine: EmbeddingEngine,
        vector_store: VectorStore,
        retriever: Retriever,
        generator: LLMGenerator,
    ):
        self.cleaner = cleaner
        self.chunker = chunker
        self.embedding_engine = embedding_engine
        self.vector_store = vector_store
        self.retriever = retriever
        self.generator = generator
        self._indexed = False

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "GenomicRAGPipeline":
        """
        Factory method para instanciar o pipeline a partir de um dicionário
        de configuração. Simplifica setup em diferentes ambientes.

        Config exemplo:
        {
            "embedding_backend": "sentence_transformers",
            "embedding_model": "paraphrase-multilingual-mpnet-base-v2",
            "llm_backend": "openai",
            "llm_model": "gpt-4o-mini",
            "top_k": 5,
            "min_score": 0.25,
        }
        """
        cleaner = TextCleaner()
        chunker = GenomicChunker(cleaner)

        embedding_engine = EmbeddingEngine(
            backend=config.get("embedding_backend", "sentence_transformers"),
            model_name=config.get("embedding_model"),
        )

        vector_store = VectorStore(
            use_faiss=config.get("use_faiss", True),
        )

        retriever = Retriever(
            vector_store=vector_store,
            embedding_engine=embedding_engine,
            top_k=config.get("top_k", 5),
            min_score=config.get("min_score", 0.25),
        )

        generator = LLMGenerator(
            backend=config.get("llm_backend", "openai"),
            model_name=config.get("llm_model"),
            temperature=config.get("temperature", 0.1),
        )

        return cls(cleaner, chunker, embedding_engine, vector_store, retriever, generator)

    def index_patient(self, genomic_json: dict[str, Any] | str) -> int:
        """
        Processa e indexa o perfil genômico de um paciente.

        Args:
            genomic_json: Dicionário ou string JSON do perfil genômico.

        Returns:
            Número de chunks indexados.
        """
        dados: dict[str, Any] = json.loads(genomic_json) if isinstance(genomic_json, str) else genomic_json

        # Cada indexação substitui o perfil anterior: sem isso, os chunks de
        # relatórios antigos continuariam no índice e poderiam ser recuperados
        # numa pergunta sobre o relatório atual.
        self.vector_store.reset()

        # 1. Chunking
        logger.info("Iniciando chunking do perfil genômico...")
        chunks = self.chunker.chunk_json(dados)

        # 2. Geração de embeddings
        logger.info(f"Gerando embeddings para {len(chunks)} chunks...")
        texts = [c.text for c in chunks]
        embeddings = self.embedding_engine.embed(texts)

        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding

        # 3. Indexação no vector store
        self.vector_store.add_chunks(chunks)
        self._indexed = True

        logger.info(f"Indexação concluída: {len(chunks)} chunks prontos para busca.")
        return len(chunks)

    def limpar_indice(self) -> None:
        """Apaga o índice do paciente (usado pelo endpoint /api/reset)."""
        self.vector_store.reset()
        self._indexed = False

    def answer(self, question: str) -> RAGResponse:
        """
        Responde uma pergunta do paciente usando o pipeline RAG completo.

        Args:
            question: Pergunta em linguagem natural do paciente.

        Returns:
            RAGResponse com resposta, chunks usados e metadados.
        """
        if not self._indexed:
            raise RuntimeError("Nenhum perfil genômico indexado. Execute index_patient() primeiro.")

        # 1. Recuperação
        retrieved_chunks = self.retriever.retrieve(question)

        # 2. Montagem do contexto
        context = self.retriever.build_context(retrieved_chunks)

        # 3. Geração
        logger.info("Gerando resposta com LLM...")
        answer_text = self.generator.generate(question, context)

        # 4. Verifica ancoragem (heurística: resposta contém termos do contexto)
        #    Roda ANTES de anexar o disclaimer, pra não distorcer o cálculo
        #    de sobreposição de termos com o texto do aviso.
        grounded = self._check_grounding(answer_text, retrieved_chunks)

        # 5. Disclaimer obrigatório de natureza informativa/não-diagnóstica.
        #    Anexado aqui, por código — não depende do LLM incluir sozinho.
        answer_text_final = answer_text + DISCLAIMER_RESPOSTA

        return RAGResponse(
            question=question,
            answer=answer_text_final,
            retrieved_chunks=retrieved_chunks,
            context_used=context,
            grounded=grounded,
        )

    def _check_grounding(self, answer: str, chunks: list[RetrievedChunk]) -> bool:
        """
        Heurística simples para verificar se a resposta está ancorada no contexto.
        Em produção, substituir por um LLM-as-judge mais robusto.
        """
        if not chunks:
            return False

        # Combina texto de todos os chunks
        combined_context = " ".join(c.chunk.text.lower() for c in chunks)
        answer_lower = answer.lower()

        # Extrai tokens significativos da resposta (>4 chars)
        answer_tokens = set(
            word for word in re.findall(r'\b\w{4,}\b', answer_lower)
            if word not in {'para', 'como', 'com', 'que', 'não', 'uma', 'mais',
                           'seu', 'sua', 'isso', 'este', 'esta', 'pelo', 'pela'}
        )

        if not answer_tokens:
            return True  # Resposta muito curta, assume ancorada

        # Calcula overlap
        overlap = sum(1 for token in answer_tokens if token in combined_context)
        overlap_ratio = overlap / len(answer_tokens)

        return overlap_ratio >= 0.3  # 30% dos termos significativos presentes no contexto
