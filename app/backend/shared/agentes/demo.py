"""
=============================================================================
Demo manual do sistema multiagente — Fase 6, Parte 2
=============================================================================
Roda o fluxo completo (Orquestrador -> Analista de Risco -> Especialista em
Protocolos -> Planejador de Resposta) contra o paciente de exemplo do
enunciado. Chama o Gemini de verdade — precisa de GEMINI_API_KEY no .env,
e por isso não faz parte da suíte automatizada (pytest) nem do CI.

Rodar de dentro de app/backend:
    python -m shared.agentes.demo
=============================================================================
"""

from pathlib import Path

from dotenv import load_dotenv

from shared.agentes.orquestracao import avaliar_paciente, formatar_saida

# Paciente de exemplo do enunciado (chave corrigida: "disponibilidade
# recursos" no texto original tem um espaço em vez de underscore).
NOVO_CASO = {
    "idade_media": 62,
    "carga_sistema": 92,
    "tempo_espera": 75,
    "fc_media": 118,
    "spo2_media": 89,
    "pa_sistolica": 100,
    "temperatura": 37.5,
    "densidade_eventos": 7,
    "eventos_24h": 5,
    "disponibilidade_recursos": 25,
}


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    print("Rodando o fluxo multiagente do CardioIA para o paciente de exemplo...\n")
    resultado = avaliar_paciente(NOVO_CASO)
    print(formatar_saida(resultado))
    print(f"\nRecomendação: {resultado.recomendacao}")


if __name__ == "__main__":
    main()
