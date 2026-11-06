const CHAVE_TEMA = 'cardioia_tema';

export function obterTemaInicial() {
  const salvo = localStorage.getItem(CHAVE_TEMA);
  if (salvo === 'dark' || salvo === 'light') return salvo;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function aplicarTema(tema) {
  document.documentElement.setAttribute('data-theme', tema);
}

export function salvarTema(tema) {
  localStorage.setItem(CHAVE_TEMA, tema);
}
