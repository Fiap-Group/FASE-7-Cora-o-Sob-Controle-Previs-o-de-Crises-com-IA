"""
=============================================================================
Validação automática das respostas do agente
=============================================================================
Checagens determinísticas, sem chamar o LLM, aplicadas a cada resposta:

  - tamanho: no máximo LIMITE_PALAVRAS palavras (sem o disclaimer);
  - clareza: média de palavras por frase abaixo de LIMITE_MEDIA_FRASE;
  - números: todo número citado precisa existir no contexto recuperado
    (evita percentual inventado);
  - jargão: termos técnicos aparecendo sem explicação entre parênteses;
  - prescrição: linguagem de medicação, dose ou conduta (sinal de alerta,
    para revisão humana: o relatório de origem também contém recomendações
    clínicas que o modelo pode repetir).

O resultado é um sinal para revisão, não um veredito clínico.
=============================================================================
"""

from typing import Any
import re

LIMITE_PALAVRAS = 130
LIMITE_MEDIA_FRASE = 20

# Termos técnicos que não devem aparecer sem tradução para o leigo.
TERMOS_TECNICOS = [
    "SNP", "alelo", "alelos", "polimorfismo", "haplogrupo", "genótipo",
    "odds ratio", "MTHFR", "CYP", "APOE", "locus", "rs\\d+",
]

# Linguagem de medicação ou conduta clínica (sinal de alerta para revisão).
TERMOS_PRESCRITIVOS = [
    "mg", "dose", "dosagem", "tome", "posologia", "prescrev", "prescrição",
    "solicite", "solicitar", "estatina", "anticoagulante",
]


def separar_disclaimer(resposta: str) -> str:
    """Remove o bloco do disclaimer (anexado por código) antes de medir a resposta."""
    return resposta.split("\n\n---")[0].strip()


def contar_palavras(texto: str) -> int:
    return len(re.findall(r"\b\w+\b", texto))


def media_palavras_por_frase(texto: str) -> float:
    frases = [f for f in re.split(r"[.!?]+|\n+", texto) if f.strip()]
    if not frases:
        return 0.0
    return sum(contar_palavras(f) for f in frases) / len(frases)


def _numeros(texto: str) -> set[str]:
    return {n.replace(",", ".") for n in re.findall(r"\d+(?:[.,]\d+)?", texto)}


def numeros_sem_fonte(resposta: str, contexto: str) -> list[str]:
    """Números citados na resposta que não aparecem no contexto recuperado."""
    citados = _numeros(resposta)
    no_contexto = _numeros(contexto)
    return sorted(n for n in citados if n not in no_contexto)


def termos_tecnicos_sem_traducao(resposta: str) -> list[str]:
    """Termo técnico é aceito quando vem seguido de explicação entre parênteses,
    como em 'alelo (uma das versões do DNA)'. Sem essa explicação, é sinalizado."""
    achados: list[str] = []
    for termo in TERMOS_TECNICOS:
        ocorrencias = re.finditer(rf"\b{termo}\b(?!\s*\()", resposta, flags=re.IGNORECASE)
        if any(True for _ in ocorrencias):
            achados.append(termo)
    return achados


def termos_prescritivos(resposta: str) -> list[str]:
    achados: list[str] = []
    for termo in TERMOS_PRESCRITIVOS:
        if re.search(rf"\b{termo}\b", resposta, flags=re.IGNORECASE):
            achados.append(termo)
    return achados


def avaliar_resposta(resposta_completa: str, contexto: str) -> dict[str, Any]:
    corpo = separar_disclaimer(resposta_completa)
    palavras = contar_palavras(corpo)
    media = round(media_palavras_por_frase(corpo), 1)
    numeros = numeros_sem_fonte(corpo, contexto)
    jargao = termos_tecnicos_sem_traducao(corpo)
    prescritivos = termos_prescritivos(corpo)
    return {
        "palavras": palavras,
        "dentro_do_limite_palavras": palavras <= LIMITE_PALAVRAS,
        "media_palavras_frase": media,
        "frases_claras": media <= LIMITE_MEDIA_FRASE,
        "numeros_sem_fonte": numeros,
        "termos_tecnicos": jargao,
        "termos_prescritivos": prescritivos,
        "ok": (
            palavras <= LIMITE_PALAVRAS
            and media <= LIMITE_MEDIA_FRASE
            and not numeros
            and not jargao
        ),
    }
