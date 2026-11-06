const CHAVE = 'cardioia_genomico';
const ESTADO_VAZIO = { perfil: null, consentimento: false, resumos: [], mensagensPorSessao: {} };

function lerEstado() {
  try {
    const bruto = localStorage.getItem(CHAVE);
    return bruto ? JSON.parse(bruto) : { ...ESTADO_VAZIO };
  } catch (_) {
    return { ...ESTADO_VAZIO };
  }
}

function salvarEstado(estado) {
  try {
    localStorage.setItem(CHAVE, JSON.stringify(estado));
  } catch (_) {
    // ambiente sem localStorage (ex: modo privado) — segue sem persistir
  }
}

export function salvarPerfilGenomico(perfilJson) {
  const estado = lerEstado();
  estado.perfil = perfilJson;
  salvarEstado(estado);
}

export function buscarPerfilGenomicoAtual() {
  return lerEstado().perfil;
}

export function temConsentimento() {
  return lerEstado().consentimento === true;
}

export function registrarConsentimento() {
  const estado = lerEstado();
  estado.consentimento = true;
  salvarEstado(estado);
}

export function criarResumo(conteudo) {
  const estado = lerEstado();
  const agora = new Date().toISOString();
  const sessaoId = Date.now();
  const resumo = { id: sessaoId, data_criacao: agora, conteudo, sessao_id: sessaoId };
  estado.resumos = [resumo, ...estado.resumos];
  estado.mensagensPorSessao[sessaoId] = [{ id: sessaoId, autor: 'ia', texto: conteudo, criado_em: agora }];
  salvarEstado(estado);
  return resumo;
}

export function buscarResumos() {
  return lerEstado().resumos;
}

export function deletarResumo(resumoId, sessaoId) {
  const estado = lerEstado();
  estado.resumos = estado.resumos.filter((r) => r.id !== resumoId);
  delete estado.mensagensPorSessao[sessaoId];
  salvarEstado(estado);
}

export function salvarMensagem(sessaoId, autor, texto) {
  const estado = lerEstado();
  const lista = estado.mensagensPorSessao[sessaoId] || [];
  lista.push({ id: Date.now(), autor, texto, criado_em: new Date().toISOString() });
  estado.mensagensPorSessao[sessaoId] = lista;
  salvarEstado(estado);
}

export function buscarMensagens(sessaoId) {
  return lerEstado().mensagensPorSessao[sessaoId] || [];
}

export function apagarDadosGenomicos() {
  salvarEstado({ ...ESTADO_VAZIO, mensagensPorSessao: {} });
}
