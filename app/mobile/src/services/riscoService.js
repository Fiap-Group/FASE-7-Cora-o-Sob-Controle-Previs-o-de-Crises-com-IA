import { avaliarRiscoCardiaco } from './api';
import { criarAvaliacaoRisco } from '../db/database';

// Chama o backend (sistema multiagente de risco cardíaco) e persiste o
// resultado localmente, igual ao padrão de gerarNovoResumo() em
// resumoService.js.
export async function avaliarRisco(dadosOperacao, usuarioId) {
  const resultado = await avaliarRiscoCardiaco(dadosOperacao, usuarioId);
  return criarAvaliacaoRisco(dadosOperacao, resultado);
}
