const CHAVE_TEMA = 'cardioia_tema';

/**
 * Lê o tema salvo pelo usuário neste navegador; se nunca escolheu, usa a preferência do sistema.
 */
export function obterTemaInicial() {
  const salvo = localStorage.getItem(CHAVE_TEMA);
  if (salvo === 'dark' || salvo === 'light') return salvo;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/**
 * Aplica o tema no documento (via atributo data-theme, lido pelo CSS).
 */
export function aplicarTema(tema) {
  document.documentElement.setAttribute('data-theme', tema);
}

/**
 * Salva a escolha de tema do usuário neste navegador.
 */
export function salvarTema(tema) {
  localStorage.setItem(CHAVE_TEMA, tema);
}
