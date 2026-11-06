// Mesmas cores de acento (primary/status) nos dois temas — só superfície, fundo e texto mudam.
// Espelha as variáveis --primary/--nivel-* etc. de app/web/src/index.css.
const status = {
  good: { bg: '#0ca30c', text: '#0b0b0b' },
  warning: { bg: '#fab219', text: '#0b0b0b' },
  serious: { bg: '#ec835a', text: '#0b0b0b' },
  critical: { bg: '#d03b3b', text: '#ffffff' },
};

export const paletaClara = {
  primary: '#2a78d6',
  primaryDark: '#184f95',
  primaryLight: '#9ec5f4',

  background: '#f9f9f7',
  surface: '#ffffff',
  border: '#e1e0d9',

  textPrimary: '#0b0b0b',
  textSecondary: '#52514e',
  textMuted: '#898781',

  white: '#ffffff',

  status,
};

export const paletaEscura = {
  primary: '#5b9bdb',
  primaryDark: '#8cbdec',
  primaryLight: '#1f3350',

  background: '#121417',
  surface: '#1c1f24',
  border: '#31353c',

  textPrimary: '#f3f2ef',
  textSecondary: '#aeada7',
  textMuted: '#787772',

  white: '#ffffff',

  status,
};

/** Mantido como padrão (tema claro) para qualquer uso fora do contexto de tema. Prefira `useTema()`. */
export const colors = paletaClara;
