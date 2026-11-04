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
