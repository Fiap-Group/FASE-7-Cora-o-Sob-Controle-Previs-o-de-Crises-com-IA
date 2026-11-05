// Deriva os dados exibidos em Ancestralidade/Riscos/Dashboard a partir do
// relatório genômico salvo pelo usuário (ver src/db/database.js).

export function mapearAncestralidade(perfil) {
  const composicao = perfil?.ancestralidade?.composicao ?? [];
  return composicao.map((item) => ({ regiao: item.origem, percentual: item.percentual }));
}

export function topAncestralidade(perfil, quantidade = 2) {
  return [...mapearAncestralidade(perfil)]
    .sort((a, b) => b.percentual - a.percentual)
    .slice(0, quantidade);
}

// Ordem importa: termos compostos (ex: "baixo-moderado") precisam vir antes
// dos termos simples que eles contêm ("baixo", "moderado"), senão o
// .includes() casa com a regra errada.
const REGRAS_NIVEL = [
  { termo: 'muito alto', nivel: 'muito alto', severidade: 4 },
  { termo: 'muito elevado', nivel: 'muito alto', severidade: 4 },
  { termo: 'critico', nivel: 'muito alto', severidade: 4 },
  { termo: 'baixo-moderado', nivel: 'moderado', severidade: 1.5 },
  { termo: 'baixo moderado', nivel: 'moderado', severidade: 1.5 },
  { termo: 'elevado', nivel: 'alto', severidade: 3 },
  { termo: 'alto', nivel: 'alto', severidade: 3 },
  { termo: 'moderado', nivel: 'moderado', severidade: 2 },
  { termo: 'baixo', nivel: 'baixo', severidade: 1 },
];

export function mapearNivelRisco(nivelRiscoRaw) {
  const normalizado = String(nivelRiscoRaw || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '');

  const regra = REGRAS_NIVEL.find((r) => normalizado.includes(r.termo));
  return regra ? { nivel: regra.nivel, severidade: regra.severidade } : { nivel: 'moderado', severidade: 2 };
}

export function mapearRiscos(perfil) {
  const riscos = perfil?.riscos_doencas ?? [];
  return riscos.map((item, index) => {
    const { nivel, severidade } = mapearNivelRisco(item.nivel_risco);
    return {
      id: item.nome ?? String(index),
      condicao: item.nome,
      nivel,
      severidade,
      descricao: item.descricao || '',
    };
  });
}

export function riscoDeMaiorSeveridade(riscosMapeados) {
  if (!riscosMapeados.length) return null;
  return [...riscosMapeados].sort((a, b) => b.severidade - a.severidade)[0];
}
