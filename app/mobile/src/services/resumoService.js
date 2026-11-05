import { criarResumo } from '../db/database';
import { perguntarAoAgente } from './api';

const PROMPT_RESUMO =
  'Gere um resumo curto (até 120 palavras) do meu perfil genômico mais recente, cobrindo os principais ' +
  'riscos de doenças e um destaque sobre ancestralidade. Use linguagem simples, acolhedora e não ' +
  'alarmista, e lembre que os resultados não substituem uma avaliação médica.';

// Em produção, o gatilho ideal é automático: toda vez que uma nova leva de
// dados do relatório chega (ex: nova semana), esta função é chamada para
// gerar o resumo, consultando o backend RAG (backend/api.py).
export async function gerarNovoResumo() {
  const resultado = await perguntarAoAgente(PROMPT_RESUMO);
  return criarResumo(resultado.answer);
}
