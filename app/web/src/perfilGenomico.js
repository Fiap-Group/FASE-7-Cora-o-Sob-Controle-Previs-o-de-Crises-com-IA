/** Mapeia a composição de ancestralidade do perfil para o formato usado nas barras. */
export function mapearAncestralidade(perfil) {
  const composicao = perfil?.ancestralidade?.composicao ?? [];
  return composicao.map((item) => ({ regiao: item.origem, percentual: item.percentual }));
}

const REGRAS_NIVEL = [
  { termo: 'muito alto', nivel: 'muito alto' },
  { termo: 'muito elevado', nivel: 'muito alto' },
  { termo: 'critico', nivel: 'muito alto' },
  { termo: 'baixo-moderado', nivel: 'moderado' },
  { termo: 'baixo moderado', nivel: 'moderado' },
  { termo: 'elevado', nivel: 'alto' },
  { termo: 'alto', nivel: 'alto' },
  { termo: 'moderado', nivel: 'moderado' },
  { termo: 'baixo', nivel: 'baixo' },
];

/** Classifica o texto de nível de risco em um dos níveis padronizados. */
export function mapearNivelRisco(nivelRiscoRaw) {
  const normalizado = String(nivelRiscoRaw || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '');

  const regra = REGRAS_NIVEL.find((r) => normalizado.includes(r.termo));
  return regra ? regra.nivel : 'moderado';
}

/** Mapeia os riscos de doenças do perfil para o formato usado nos cartões de risco. */
export function mapearRiscos(perfil) {
  const riscos = perfil?.riscos_doencas ?? [];
  return riscos.map((item, index) => ({
    id: item.nome ?? String(index),
    condicao: item.nome,
    nivel: mapearNivelRisco(item.nivel_risco),
    descricao: item.descricao || '',
  }));
}
