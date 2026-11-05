// URL do backend FastAPI. Em produção (Vercel), vem de VITE_API_URL
// (configurada no painel do projeto). Sem essa variável, usa o localhost
// de desenvolvimento — mesmo padrão de app/mobile/src/services/api.js,
// mas com o prefixo VITE_ (convenção do Vite, não EXPO_PUBLIC_*).
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

function mensagemDeErro(corpoErro, mensagemPadrao) {
  return corpoErro.details || corpoErro.error || mensagemPadrao;
}

// Busca a última leitura publicada pelo ESP32 via MQTT, guardada em
// memória pelo backend (GET /api/risco/leitura-iot).
export async function buscarLeituraIot() {
  const resposta = await fetch(`${API_URL}/api/risco/leitura-iot`);

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(mensagemDeErro(erro, 'Falha ao buscar a leitura do sensor.'));
  }

  return resposta.json();
}

// Envia os dados de operação hospitalar ao sistema multiagente de previsão
// de risco cardíaco (POST /api/risco/avaliar) e retorna { probabilidade,
// classificacao, protocolos, recomendacao }.
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

// Conta de usuário (src/modules/auth do backend) — compartilhada com o
// app mobile, por isso não fica no localStorage (ver sessao.js, que só
// guarda a sessão lembrada NESTE navegador, não a conta em si).
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

// "Ficha de jogador": conta + avaliação de risco mais recente em destaque +
// histórico curto (ver app/backend/src/modules/perfil).
export async function buscarPerfil(usuarioId) {
  const resposta = await fetch(`${API_URL}/api/perfil/${usuarioId}`);

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(mensagemDeErro(erro, 'Falha ao buscar o perfil.'));
  }

  return resposta.json();
}
