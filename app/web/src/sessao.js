const CHAVE_SESSAO = 'cardioia_sessao';

export function salvar(usuario) {
  localStorage.setItem(CHAVE_SESSAO, JSON.stringify(usuario));
}

export function obter() {
  const salvo = localStorage.getItem(CHAVE_SESSAO);
  return salvo ? JSON.parse(salvo) : null;
}

export function limpar() {
  localStorage.removeItem(CHAVE_SESSAO);
}
