import { Platform } from 'react-native';
import { buscarPerfilGenomicoAtual } from '../db/database';

// Backend RAG (ver /backend). Em produção (front publicado na nuvem), a URL
// vem de EXPO_PUBLIC_API_URL, apontando para o túnel do backend. Sem essa
// variável, usa o localhost de desenvolvimento. O emulador Android não
// enxerga "localhost" da máquina host, por isso usa 10.0.2.2 nesse caso.
const API_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  Platform.select({
    android: 'http://10.0.2.2:5000',
    default: 'http://localhost:5000',
  });

let indexadoNestaSessao = false;

// Pede ao backend que esqueça o índice do paciente. Não lança erro se o
// backend estiver fora do ar: os dados do dispositivo são apagados mesmo assim.
export async function apagarIndiceNoBackend() {
  try {
    await fetch(`${API_URL}/api/reset`, { method: 'POST' });
  } catch (_) {
    // backend indisponível: nada a apagar na memória dele
  }
  indexadoNestaSessao = false;
}

// O backend devolve { error, details }: "details" costuma ter a explicação
// mais útil (ex: "cota diária esgotada"), então preferimos ela quando existe.
function mensagemDeErro(corpoErro, mensagemPadrao) {
  return corpoErro.details || corpoErro.error || mensagemPadrao;
}

// Indexa o relatório genômico do usuário no backend RAG. Chamado explicitamente
// pela tela Ancestralidade quando o usuário envia um relatório novo.
export async function indexarRelatorio(perfilJson) {
  const resposta = await fetch(`${API_URL}/api/index`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(perfilJson),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.error || 'Falha ao indexar o relatório genômico no backend.');
  }

  indexadoNestaSessao = true;
  return resposta.json();
}

async function garantirIndexacao() {
  if (indexadoNestaSessao) return;

  const perfilSalvo = await buscarPerfilGenomicoAtual();
  if (!perfilSalvo) {
    throw new Error('Nenhum relatório enviado ainda. Vá até a aba Ancestralidade e envie seu relatório genômico.');
  }

  await indexarRelatorio(perfilSalvo);
}

async function chamarChat(pergunta) {
  return fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: pergunta }),
  });
}

// Envia uma pergunta ao agente RAG e retorna { answer, sources, grounded }.
// Lança erro se o backend (backend/api.py) não estiver rodando, sem chave de
// LLM configurada, ou se nenhum relatório tiver sido enviado ainda.
export async function perguntarAoAgente(pergunta) {
  await garantirIndexacao();

  let resposta = await chamarChat(pergunta);

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));

    // O índice do RAG vive em memória no backend: se o processo foi
    // reiniciado (ex: derrubou e subiu o api.py de novo) mas o app ainda
    // acha que já indexou nesta sessão, reindexa a partir do relatório
    // salvo no SQLite e tenta de novo, uma vez, antes de desistir.
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

// Envia os dados de operação hospitalar ao sistema multiagente de previsão
// de risco cardíaco e retorna { probabilidade, classificacao, protocolos,
// recomendacao }. Pode levar vários segundos: a resposta passa por uma
// cadeia de agentes (Orquestrador -> Analista de Risco -> Especialista em
// Protocolos -> Planejador de Resposta), cada um com sua própria chamada ao
// Gemini.
export async function avaliarRiscoCardiaco(dadosOperacao) {
  const resposta = await fetch(`${API_URL}/api/risco/avaliar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dadosOperacao),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(mensagemDeErro(erro, 'Falha ao avaliar o risco cardíaco.'));
  }

  return resposta.json();
}

// Busca a última leitura publicada pelo ESP32 via MQTT (fc_media,
// pa_sistolica, spo2_media), guardada em memória pelo backend. Não dispara
// nenhuma avaliação de risco — só lê o que já está guardado no backend. Se
// o sensor nunca publicou nada ainda, volta { conectado: false, ... null }.
export async function buscarLeituraIot() {
  const resposta = await fetch(`${API_URL}/api/risco/leitura-iot`);

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(mensagemDeErro(erro, 'Falha ao buscar a leitura do sensor.'));
  }

  return resposta.json();
}

// Conta de usuário (src/modules/auth do backend) — compartilhada com o
// app web, por isso não fica no SQLite local (ver db/database.js:
// definirSessao/obterUsuarioLogado, que só guardam a sessão lembrada
// NESTE aparelho, não a conta em si).
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
