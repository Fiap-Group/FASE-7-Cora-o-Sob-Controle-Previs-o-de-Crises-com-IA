import { avaliarRiscoCardiaco } from './api';
import { criarAvaliacaoRisco } from '../db/database';

/** Solicita ao backend a avaliação de risco cardíaco e salva o resultado localmente. */
export async function avaliarRisco(dadosOperacao, usuarioId) {
  const resultado = await avaliarRiscoCardiaco(dadosOperacao, usuarioId);
  return criarAvaliacaoRisco(dadosOperacao, resultado);
}
