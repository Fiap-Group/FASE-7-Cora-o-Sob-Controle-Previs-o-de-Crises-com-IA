// A conta mora no backend (POST /api/auth/*, compartilhada com o app
// mobile via o mesmo endpoint) — isto aqui só lembra quem está logado
// NESTE navegador, pra não pedir login de novo a cada reload. Mesmo
// papel do SQLite local em app/mobile/src/db/database.js
// (definirSessao/obterUsuarioLogado), só que em localStorage.
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
