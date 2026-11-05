import { criarResumo } from './genomicoDb';
import { perguntarAoAgente } from './api';

const PROMPT_RESUMO =
  'Gere um resumo curto (até 120 palavras) do meu perfil genômico mais recente, cobrindo os principais ' +
  'riscos de doenças e um destaque sobre ancestralidade. Use linguagem simples, acolhedora e não ' +
  'alarmista, e lembre que os resultados não substituem uma avaliação médica.';

/** Gera um novo resumo do perfil genômico consultando o agente e salva o resultado. */
export async function gerarNovoResumo() {
  const resultado = await perguntarAoAgente(PROMPT_RESUMO);
  return criarResumo(resultado.answer);
}
