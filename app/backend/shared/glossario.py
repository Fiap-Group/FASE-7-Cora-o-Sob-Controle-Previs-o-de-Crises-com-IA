"""
=============================================================================
Glossário de termos técnicos — traduções para o paciente leigo
=============================================================================
Termos que aparecem nos relatórios genéticos e a explicação em linguagem
simples que o agente deve usar. Injetado no prompt do sistema (ver
prompts.py), para que o modelo use estas traduções prontas em vez de
inventar uma explicação diferente a cada resposta.
=============================================================================
"""

GLOSSARIO = {
    "gene": "trecho do DNA que funciona como uma receita para o corpo produzir alguma substância",
    "DNA": "o 'manual de instruções' do corpo, guardado em cada célula",
    "variante": "diferença no DNA em relação ao padrão mais comum da população",
    "polimorfismo": "variação comum no DNA, que existe em muitas pessoas e geralmente não causa problemas",
    "SNP": "uma pequena troca de uma letra do DNA",
    "alelo": "uma das versões de um mesmo trecho do DNA (cada pessoa herda uma de cada pai)",
    "genótipo": "a combinação de versões do DNA que uma pessoa tem em um trecho específico",
    "haplogrupo": "grupo de famílias de DNA que se formou ao longo de muitas gerações, usado para estudar a origem ancestral",
    "MTHFR": "gene que ajuda o corpo a processar a vitamina B9 (ácido fólico)",
    "CYP": "família de genes que ajuda o fígado a processar medicamentos e outras substâncias",
    "rs": "código de identificação de uma variação no DNA, usado por cientistas para localizá-la",
    "risco relativo": "quanto a chance de algo acontecer aumenta ou diminui em comparação com a média da população",
    "odds ratio": "uma forma de medir o quanto um fator aumenta ou diminui a chance de uma condição, em comparação com a média",
    "hereditário": "passado de pais para filhos pelo DNA",
    "predisposição": "tendência, e não certeza, de desenvolver algo ao longo da vida",
}


def glossario_para_prompt() -> str:
    linhas = [f'- "{termo}": {explicacao}' for termo, explicacao in GLOSSARIO.items()]
    return "\n".join(linhas)
