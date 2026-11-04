"""Testes das checagens automáticas de validacao.py (lógica pura, sem LLM)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "avaliacao"))

from validacao import (  # noqa: E402
    avaliar_resposta,
    numeros_sem_fonte,
    termos_prescritivos,
    termos_tecnicos_sem_traducao,
)

DISCLAIMER = "\n\n---\n⚠️ Isto é uma informação, não um diagnóstico. Converse com seu médico."
CONTEXTO = "Risco 3,5x acima da média. Chance de 38% no seu perfil; média da população 11%."


def test_numero_que_existe_no_contexto_nao_e_sinalizado():
    assert numeros_sem_fonte("Sua chance é de 38%.", CONTEXTO) == []


def test_numero_inventado_e_sinalizado():
    assert numeros_sem_fonte("Sua chance é de 75%.", CONTEXTO) == ["75"]


def test_virgula_e_ponto_decimal_sao_equivalentes():
    assert numeros_sem_fonte("Risco de 3.5x.", CONTEXTO) == []


def test_termo_tecnico_com_explicacao_entre_parenteses_e_aceito():
    texto = "O alelo (uma das versões do DNA) influencia isso."
    assert termos_tecnicos_sem_traducao(texto) == []


def test_termo_tecnico_sem_traducao_e_sinalizado():
    assert "polimorfismo" in termos_tecnicos_sem_traducao("Você tem um polimorfismo comum.")


def test_linguagem_prescritiva_e_sinalizada():
    assert "mg" in termos_prescritivos("Tome 50 mg por dia.")


def test_disclaimer_nao_conta_no_limite_de_palavras():
    corpo = "Sua chance é de 38%. Isso é um sinal de atenção."
    resultado = avaliar_resposta(corpo + DISCLAIMER, CONTEXTO)
    assert resultado["palavras"] == avaliar_resposta(corpo, CONTEXTO)["palavras"]


def test_resposta_longa_reprova_no_limite_de_palavras():
    longa = " ".join(["palavra"] * 200) + "."
    assert avaliar_resposta(longa, CONTEXTO)["dentro_do_limite_palavras"] is False


def test_resposta_curta_e_clara_passa():
    resposta = "Sua chance é de 38%. Isso não é destino. Converse com seu médico." + DISCLAIMER
    resultado = avaliar_resposta(resposta, CONTEXTO)
    assert resultado["ok"] is True
