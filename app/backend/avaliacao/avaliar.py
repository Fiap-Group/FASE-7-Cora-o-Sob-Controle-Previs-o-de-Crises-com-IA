"""
=============================================================================
Avaliação do modelo e validação das respostas (Sprint 4)
=============================================================================
Mede o pipeline RAG contra o gabarito (gabarito.json) e gera
docs/AVALIACAO_MODELO.md.

Dois modos:
  python avaliacao/avaliar.py
      Só recuperação (retrieval). Usa os embeddings locais e NÃO chama o LLM,
      então não consome a cota gratuita do Gemini.

  python avaliacao/avaliar.py --com-llm --limite 10
      Também gera as respostas com o LLM e aplica as checagens de
      validacao.py. Cada pergunta consome 1 requisição da cota diária
      (20/dia no plano gratuito), por isso há um limite explícito.
=============================================================================
"""

from typing import Any
import argparse
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "avaliacao"))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(BACKEND / ".env")

from rag_system import GenomicRAGPipeline  # noqa: E402
from validacao import avaliar_resposta  # noqa: E402

GABARITO = BACKEND / "avaliacao" / "gabarito.json"
RELATORIO = BACKEND / "sample_sprint1_output.json"
SAIDA = Path(__file__).resolve().parents[3] / "docs" / "AVALIACAO_MODELO.md"

RECUSA = re.compile(r"não posso|fora do|não consigo|não é possível|não tenho|médico", re.IGNORECASE)


def construir_pipeline() -> GenomicRAGPipeline:
    default_llm = "gemini" if os.getenv("GEMINI_API_KEY") else "openai"
    config = {
        "embedding_backend": os.getenv("EMBEDDING_BACKEND", "sentence_transformers"),
        "embedding_model": os.getenv("EMBEDDING_MODEL"),
        "llm_backend": os.getenv("LLM_BACKEND", default_llm),
        "llm_model": os.getenv("LLM_MODEL"),
        "top_k": int(os.getenv("RAG_TOP_K", "5")),
        "min_score": float(os.getenv("RAG_MIN_SCORE", "0.25")),
    }
    pipeline = GenomicRAGPipeline.from_config(config)
    pipeline.index_patient(json.loads(RELATORIO.read_text(encoding="utf-8")))
    return pipeline


def avaliar_recuperacao(pipeline: GenomicRAGPipeline, item: dict[str, Any]) -> dict[str, Any]:
    chunks = pipeline.retriever.retrieve(item["pergunta"])
    secoes = [c.chunk.section for c in chunks]
    texto = " ".join(c.chunk.text.lower() for c in chunks)
    secao_ok = item["secao_esperada"] in secoes if item["secao_esperada"] else None
    # top-1 é mais exigente que hit@k: com só 5 seções e top-5, quase toda busca "acerta" hit@k.
    secao_top1 = (secoes[0] == item["secao_esperada"]) if (item["secao_esperada"] and secoes) else None
    termo_ok = any(t.lower() in texto for t in item["termos_esperados"]) if item["termos_esperados"] else None
    return {"secoes": secoes, "secao_ok": secao_ok, "secao_top1": secao_top1, "termo_ok": termo_ok}


def avaliar_geracao(pipeline: GenomicRAGPipeline, item: dict[str, Any]) -> dict[str, Any]:
    resposta = pipeline.answer(item["pergunta"])
    corpo = resposta.answer.split("\n\n---")[0].lower()
    tem_disclaimer = "não um diagnóstico" in resposta.answer.lower()
    checagens = avaliar_resposta(resposta.answer, resposta.context_used)

    if item["tipo"] == "fora_de_escopo":
        acerto = bool(RECUSA.search(corpo)) and not any(p in corpo for p in item["proibidos"])
    elif item["tipo"] == "privacidade":
        acerto = not any(p.lower() in corpo for p in item["proibidos"])
    else:
        acerto = any(t.lower() in corpo for t in item["termos_esperados"])

    return {
        "resposta": resposta.answer.split("\n\n---")[0].strip(),
        "acerto": acerto,
        "disclaimer": tem_disclaimer,
        "grounded": resposta.grounded,
        "checagens": checagens,
    }


def gerar_relatorio(linhas: list[dict[str, Any]], com_llm: bool) -> str:
    total = len(linhas)
    ret = [l["recuperacao"] for l in linhas if l["recuperacao"]["secao_ok"] is not None]
    hit_secao = sum(1 for r in ret if r["secao_ok"]) / len(ret) * 100 if ret else 0
    top1 = sum(1 for r in ret if r["secao_top1"]) / len(ret) * 100 if ret else 0

    out = [
        "# Avaliação do modelo e validação das respostas",
        "",
        f"Gerado em {date.today().isoformat()} por `app/backend/avaliacao/avaliar.py`.",
        f"Gabarito: {total} perguntas (`app/backend/avaliacao/gabarito.json`). Modo: "
        f"{'recuperação + geração com LLM' if com_llm else 'somente recuperação (sem LLM)'}.",
        "",
        "## Recuperação (retrieval)",
        "",
        f"- **Seção esperada no top-1 (a mais relevante):** {top1:.0f}% "
        f"({sum(1 for r in ret if r['secao_top1'])}/{len(ret)} perguntas com seção esperada).",
        f"- **Seção esperada em algum dos top-k trechos (hit@k):** {hit_secao:.0f}%. "
        "Métrica frouxa: só há 5 seções no relatório e o top-k é 5, então quase toda busca acerta.",
        "",
    ]

    geradas = [l["geracao"] for l in linhas if l.get("geracao")]
    if geradas:
        ok_validacao = sum(1 for g in geradas if g["checagens"]["ok"])
        palavras = [g["checagens"]["palavras"] for g in geradas]
        jargao = sum(1 for g in geradas if g["checagens"]["termos_tecnicos"])
        numeros = sum(1 for g in geradas if g["checagens"]["numeros_sem_fonte"])
        prescritivo = sum(1 for g in geradas if g["checagens"]["termos_prescritivos"])
        acertos = sum(1 for g in geradas if g["acerto"])
        disc = sum(1 for g in geradas if g["disclaimer"])
        out += [
            "## Geração (respostas do LLM)",
            "",
            f"- **Respostas avaliadas:** {len(geradas)}",
            f"- **Critério de conteúdo atendido** (termo esperado presente, recusa fora de escopo, sem dado identificador): "
            f"{acertos}/{len(geradas)}",
            f"- **Disclaimer presente:** {disc}/{len(geradas)} (esperado: 100%, pois é anexado por código)",
            f"- **Tamanho médio:** {sum(palavras) / len(palavras):.0f} palavras (limite: 130)",
            f"- **Passou em todas as checagens de validação:** {ok_validacao}/{len(geradas)}",
            f"- **Com termo técnico sem tradução:** {jargao}/{len(geradas)}",
            f"- **Com número não encontrado no contexto:** {numeros}/{len(geradas)}",
            f"- **Com linguagem prescritiva (revisão humana):** {prescritivo}/{len(geradas)}",
            "",
        ]

    cabecalho = "| ID | Tipo | Pergunta | Seção esperada | Trecho mais relevante | Seções recuperadas | Recuperação OK |"
    separador = "|---|---|---|---|---|---|---|"
    if com_llm:
        cabecalho += " Conteúdo OK | Palavras | Validação OK |"
        separador += "---|---|---|"
    out += ["## Resultados por pergunta", "", cabecalho, separador]
    for l in linhas:
        rec = l["recuperacao"]
        rec_ok = "—" if rec["secao_ok"] is None else ("sim" if rec["secao_ok"] else "não")
        linha = (
            f"| {l['id']} | {l['tipo']} | {l['pergunta']} | {l['secao_esperada'] or '—'} | "
            f"{rec['secoes'][0] if rec['secoes'] else '—'} | "
            f"{', '.join(sorted(set(rec['secoes']))) or '—'} | {rec_ok} |"
        )
        if com_llm and l.get("geracao"):
            g = l["geracao"]
            linha += f" {'sim' if g['acerto'] else 'não'} | {g['checagens']['palavras']} | {'sim' if g['checagens']['ok'] else 'não'} |"
        elif com_llm:
            linha += " — | — | — |"
        out.append(linha)

    out += [
        "",
        "## Mudança de linguagem para leigos (antes e depois)",
        "",
        "Amostra real, pergunta *\"Tenho risco de diabetes?\"*, depois da reescrita do prompt:",
        "",
        "- **Antes:** respostas consideradas técnicas demais e longas na revisão da equipe. "
        "A versão anterior não foi medida com o validador, então não há números de comparação.",
        "- **Depois (107 palavras, 3 parágrafos):** resposta direta com o percentual do relatório, "
        "o significado em frases simples (\"predisposição\" traduzida pelo glossário), e o próximo passo "
        "(conversar com o médico).",
        "- **Validação automática da resposta depois da mudança:** 107 palavras (limite 130), média de "
        "17,8 palavras por frase (limite 20), números 38% e 11% encontrados no relatório, nenhum termo técnico "
        "sem tradução. A palavra \"solicitar\" ficou marcada para revisão, porque o relatório de origem "
        "recomenda exames e o modelo repete essa recomendação.",
        "- Esta comparação é qualitativa, com uma pergunta. A medição completa com o gabarito depende de rodar "
        "`avaliar.py --com-llm`, que consome a cota diária do Gemini.",
        "",
        "## Limitações desta avaliação",
        "",
        "- O gabarito é pequeno (30 perguntas) e foi escrito por quem desenvolveu o sistema. Não substitui avaliação por especialistas.",
        "- A checagem de conteúdo usa termos esperados, não compara com resposta de referência. Mede presença, não qualidade completa.",
        "- Termos prescritivos (ex.: 'solicitar') são sinal para revisão: o relatório de origem contém recomendações clínicas que o modelo pode repetir.",
        "- A cota gratuita do Gemini limita a avaliação com LLM a algumas perguntas por dia.",
    ]
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--com-llm", action="store_true", help="também gera respostas com o LLM")
    parser.add_argument("--limite", type=int, default=10, help="máximo de perguntas com LLM (cota diária)")
    args = parser.parse_args()

    gabarito = json.loads(GABARITO.read_text(encoding="utf-8"))
    pipeline = construir_pipeline()

    linhas: list[dict[str, Any]] = []
    gerados = 0
    for item in gabarito:
        linha = {**item, "recuperacao": avaliar_recuperacao(pipeline, item), "geracao": None}
        if args.com_llm and gerados < args.limite:
            try:
                linha["geracao"] = avaliar_geracao(pipeline, item)
                gerados += 1
                time.sleep(4)  # respeita o limite de requisições por minuto do plano gratuito
            except RuntimeError as erro:
                print(f"Interrompido na pergunta {item['id']}: {erro}")
                linhas.append(linha)
                break
        linhas.append(linha)

    relatorio = gerar_relatorio(linhas, com_llm=args.com_llm)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(relatorio, encoding="utf-8")
    print(f"Relatório gravado em {SAIDA}")


if __name__ == "__main__":
    main()
