import { buscarPerfilGenomicoAtual } from './genomicoDb';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
const HEADERS_PADRAO = { 'X-Client-Platform': 'web' };

/**
 * Monta a mensagem de erro a partir do corpo da resposta, com um texto padrão de reserva.
 */
function mensagemDeErro(corpoErro, mensagemPadrao) {
  return corpoErro.details || corpoErro.error || mensagemPadrao;
}

let indexadoNestaSessao = false;

/**
 * Solicita ao backend que apague o índice do relatório genômico, ignorando falhas de conexão.
 */
export async function apagarIndiceNoBackend() {
  try {
    await fetch(`${API_URL}/api/reset`, { method: 'POST', headers: HEADERS_PADRAO });
  } catch (_) {
    // best-effort: a limpeza local acontece de qualquer forma
  }
  indexadoNestaSessao = false;
}

/**
 * Indexa o relatório genômico no backend RAG.
 */
export async function indexarRelatorio(perfilJson) {
  const resposta = await fetch(`${API_URL}/api/index`, {
    method: 'POST',
    headers: { ...HEADERS_PADRAO, 'Content-Type': 'application/json' },
    body: JSON.stringify(perfilJson),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.error || 'Falha ao indexar o relatório genômico no backend.');
  }

  indexadoNestaSessao = true;
  return resposta.json();
}

/**
 * Garante que o relatório salvo neste navegador esteja indexado no backend antes de consultar o agente.
 */
async function garantirIndexacao() {
  if (indexadoNestaSessao) return;

  const perfilSalvo = buscarPerfilGenomicoAtual();
  if (!perfilSalvo) {
    throw new Error('Nenhum relatório enviado ainda. Vá até a aba Ancestralidade e envie seu relatório genômico.');
  }

  await indexarRelatorio(perfilSalvo);
}

/**
 * Envia a pergunta ao endpoint de chat do backend.
 */
async function chamarChat(pergunta) {
  return fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { ...HEADERS_PADRAO, 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: pergunta }),
  });
}

/**
 * Envia uma pergunta ao agente RAG e retorna a resposta, reindexando o relatório se necessário.
 */
export async function perguntarAoAgente(pergunta) {
  await garantirIndexacao();

  let resposta = await chamarChat(pergunta);

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));

    const perdeuIndiceNoBackend = resposta.status === 400 && /indexado/i.test(erro.error || '');
    if (perdeuIndiceNoBackend) {
      indexadoNestaSessao = false;
      await garantirIndexacao();
      resposta = await chamarChat(pergunta);
    }

    if (!resposta.ok) {
      const erroFinal = await resposta.json().catch(() => ({}));
      throw new Error(mensagemDeErro(erroFinal, 'Falha ao consultar o agente.'));
    }
  }

  return resposta.json();
}

/**
 * Busca a última leitura publicada pelo sensor ESP32 via MQTT.
 */
export async function buscarLeituraIot() {
  const resposta = await fetch(`${API_URL}/api/risco/leitura-iot`, { headers: HEADERS_PADRAO });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(mensagemDeErro(erro, 'Falha ao buscar a leitura do sensor.'));
  }

  return resposta.json();
}

/**
 * Envia os dados de operação hospitalar para o sistema multiagente avaliar o risco cardíaco.
 */
export async function avaliarRiscoCardiaco(dadosOperacao, usuarioId) {
  const resposta = await fetch(`${API_URL}/api/risco/avaliar`, {
    method: 'POST',
    headers: { ...HEADERS_PADRAO, 'Content-Type': 'application/json' },
    body: JSON.stringify(usuarioId != null ? { ...dadosOperacao, usuario_id: usuarioId } : dadosOperacao),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(mensagemDeErro(erro, 'Falha ao avaliar o risco cardíaco.'));
  }

  return resposta.json();
}

/**
 * Cadastra uma nova conta de usuário.
 */
export async function cadastrar(email, senha) {
  const resposta = await fetch(`${API_URL}/api/auth/cadastro`, {
    method: 'POST',
    headers: { ...HEADERS_PADRAO, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, senha }),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(mensagemDeErro(erro, 'Falha ao criar a conta.'));
  }

  return resposta.json();
}

/**
 * Autentica o usuário com e-mail e senha.
 */
export async function login(email, senha) {
  const resposta = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { ...HEADERS_PADRAO, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, senha }),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(mensagemDeErro(erro, 'Falha ao entrar na conta.'));
  }

  return resposta.json();
}

/**
 * Define o nickname de um usuário recém-cadastrado.
 */
export async function definirNickname(usuarioId, nickname) {
  const resposta = await fetch(`${API_URL}/api/auth/nickname`, {
    method: 'POST',
    headers: { ...HEADERS_PADRAO, 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario_id: usuarioId, nickname }),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(mensagemDeErro(erro, 'Falha ao salvar o nickname.'));
  }

  return resposta.json();
}

/**
 * Busca o perfil do usuário, com a avaliação de risco mais recente e o histórico.
 */
export async function buscarPerfil(usuarioId) {
  const resposta = await fetch(`${API_URL}/api/perfil/${usuarioId}`, { headers: HEADERS_PADRAO });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(mensagemDeErro(erro, 'Falha ao buscar o perfil.'));
  }

  return resposta.json();
}
