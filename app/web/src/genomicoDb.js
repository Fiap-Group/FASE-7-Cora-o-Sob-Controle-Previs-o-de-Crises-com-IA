const CHAVE = 'cardioia_genomico';
const ESTADO_VAZIO = { perfil: null, consentimento: false, resumos: [], mensagensPorSessao: {} };

/** Lê o estado genômico salvo neste navegador (relatório, resumos e conversas). */
function lerEstado() {
  try {
    const bruto = localStorage.getItem(CHAVE);
    return bruto ? JSON.parse(bruto) : { ...ESTADO_VAZIO };
  } catch (_) {
    return { ...ESTADO_VAZIO };
  }
}

/** Persiste o estado genômico neste navegador. */
function salvarEstado(estado) {
  try {
    localStorage.setItem(CHAVE, JSON.stringify(estado));
  } catch (_) {
    // ambiente sem localStorage (ex: modo privado) — segue sem persistir
  }
}

/** Salva o relatório genômico mais recente enviado pelo usuário. */
export function salvarPerfilGenomico(perfilJson) {
  const estado = lerEstado();
  estado.perfil = perfilJson;
  salvarEstado(estado);
}

/** Busca o relatório genômico salvo, ou null se nenhum foi enviado ainda. */
export function buscarPerfilGenomicoAtual() {
  return lerEstado().perfil;
}

/** Verifica se o usuário já autorizou o uso dos dados genômicos pela IA. */
export function temConsentimento() {
  return lerEstado().consentimento === true;
}

/** Registra que o usuário autorizou o uso dos dados genômicos pela IA. */
export function registrarConsentimento() {
  const estado = lerEstado();
  estado.consentimento = true;
  salvarEstado(estado);
}

/** Cria um novo resumo, com uma sessão de conversa própria já contendo o resumo como primeira mensagem. */
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

/** Busca todos os resumos salvos, do mais recente para o mais antigo. */
export function buscarResumos() {
  return lerEstado().resumos;
}

/** Remove um resumo e toda a conversa associada a ele. */
export function deletarResumo(resumoId, sessaoId) {
  const estado = lerEstado();
  estado.resumos = estado.resumos.filter((r) => r.id !== resumoId);
  delete estado.mensagensPorSessao[sessaoId];
  salvarEstado(estado);
}

/** Salva uma mensagem na sessão de chat informada. */
export function salvarMensagem(sessaoId, autor, texto) {
  const estado = lerEstado();
  const lista = estado.mensagensPorSessao[sessaoId] || [];
  lista.push({ id: Date.now(), autor, texto, criado_em: new Date().toISOString() });
  estado.mensagensPorSessao[sessaoId] = lista;
  salvarEstado(estado);
}

/** Busca todas as mensagens de uma sessão de chat, em ordem cronológica. */
export function buscarMensagens(sessaoId) {
  return lerEstado().mensagensPorSessao[sessaoId] || [];
}

/** Apaga do navegador o relatório, o consentimento, os resumos e as conversas. */
export function apagarDadosGenomicos() {
  salvarEstado({ ...ESTADO_VAZIO, mensagensPorSessao: {} });
}
