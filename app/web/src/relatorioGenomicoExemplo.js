export default {
  paciente: {
    id: 'PAC-2024-001',
    nome: 'Carlos Silva',
    data_nascimento: '1985-03-15',
    sexo: 'masculino',
    data_exame: '2024-11-20',
    laboratorio: 'Laboratório Parceiro',
  },
  ancestralidade: {
    composicao: [
      { origem: 'Europeia', percentual: 68 },
      { origem: 'Africana', percentual: 22 },
      { origem: 'Ameríndia', percentual: 10 },
    ],
  },
  riscos_doencas: [
    {
      nome: 'Diabetes Tipo 2',
      nivel_risco: 'Elevado',
      descricao:
        'Risco 3.5x acima da média populacional. O gene TCF7L2 é o principal fator de risco genético para DM2 identificado até hoje. A combinação com ancestralidade ameríndia amplifica o risco.',
    },
    {
      nome: 'Doença Cardiovascular',
      nivel_risco: 'Moderado',
      descricao:
        'Risco 1.6x acima da média. Variantes no locus 9p21 associadas a IAM e angina instável. Responde bem a estatinas.',
    },
    {
      nome: 'Câncer de Mama',
      nivel_risco: 'Baixo-Moderado',
      descricao:
        'Risco próximo à média populacional. Ausência de variantes BRCA1/BRCA2 patogênicas. Rastreamento padrão recomendado.',
    },
    {
      nome: 'Doença de Alzheimer',
      nivel_risco: 'Moderado',
      descricao:
        'Portador do alelo APOE ε3/ε4 (heterozigoto). Risco aumentado mas não determinístico.',
    },
    {
      nome: 'Trombose Venosa Profunda',
      nivel_risco: 'Baixo',
      descricao: 'Fator V Leiden negativo. Risco próximo à média populacional.',
    },
  ],
};
