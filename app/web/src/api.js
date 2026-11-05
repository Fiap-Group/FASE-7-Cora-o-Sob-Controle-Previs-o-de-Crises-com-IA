const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * Monta a mensagem de erro a partir do corpo da resposta, com um texto padrão de reserva.
 */
function mensagemDeErro(corpoErro, mensagemPadrao) {
  return corpoErro.details || corpoErro.error || mensagemPadrao;
}

/**
 * Busca a última leitura publicada pelo sensor ESP32 via MQTT.
 */
export async function buscarLeituraIot() {
  const resposta = await fetch(`${API_URL}/api/risco/leitura-iot`);

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
    headers: { 'Content-Type': 'application/json' },
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
    headers: { 'Content-Type': 'application/json' },
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
    headers: { 'Content-Type': 'application/json' },
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
    headers: { 'Content-Type': 'application/json' },
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
  const resposta = await fetch(`${API_URL}/api/perfil/${usuarioId}`);

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(mensagemDeErro(erro, 'Falha ao buscar o perfil.'));
  }

  return resposta.json();
}
