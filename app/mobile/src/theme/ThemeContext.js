import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { Appearance } from 'react-native';
import { initDatabase, obterConfiguracao, salvarConfiguracao } from '../db/database';
import { paletaClara, paletaEscura } from './colors';

const CHAVE_TEMA = 'tema';
const ThemeContext = createContext(null);

/** Provedor do tema claro/escuro: parte da preferência do sistema e persiste a escolha manual do usuário. */
export function ThemeProvider({ children }) {
  const [esquema, setEsquema] = useState(Appearance.getColorScheme() === 'dark' ? 'dark' : 'light');

  useEffect(() => {
    (async () => {
      await initDatabase();
      const salvo = await obterConfiguracao(CHAVE_TEMA);
      if (salvo === 'dark' || salvo === 'light') {
        setEsquema(salvo);
      }
    })();
  }, []);

  const alternarTema = () => {
    setEsquema((atual) => {
      const novo = atual === 'dark' ? 'light' : 'dark';
      salvarConfiguracao(CHAVE_TEMA, novo);
      return novo;
    });
  };

  const valor = useMemo(
    () => ({
      esquema,
      colors: esquema === 'dark' ? paletaEscura : paletaClara,
      alternarTema,
    }),
    [esquema]
  );

  return <ThemeContext.Provider value={valor}>{children}</ThemeContext.Provider>;
}

/** Hook de acesso ao tema atual (`colors`, `esquema` e `alternarTema`). */
export function useTema() {
  const contexto = useContext(ThemeContext);
  if (!contexto) {
    throw new Error('useTema precisa ser usado dentro de um ThemeProvider');
  }
  return contexto;
}
