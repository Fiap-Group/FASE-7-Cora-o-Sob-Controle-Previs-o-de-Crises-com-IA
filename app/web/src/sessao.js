const CHAVE_SESSAO = 'cardioia_sessao';

/**
 * Salva o usuário autenticado na sessão deste navegador.
 */
export function salvar(usuario) {
  localStorage.setItem(CHAVE_SESSAO, JSON.stringify(usuario));
}

/**
 * Obtém o usuário salvo na sessão deste navegador, se houver.
 */
export function obter() {
  const salvo = localStorage.getItem(CHAVE_SESSAO);
  return salvo ? JSON.parse(salvo) : null;
}

/**
 * Remove a sessão salva deste navegador.
 */
export function limpar() {
  localStorage.removeItem(CHAVE_SESSAO);
}
