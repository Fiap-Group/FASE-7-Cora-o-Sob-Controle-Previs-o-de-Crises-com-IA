import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { encerrarSessao, obterUsuarioLogado } from '../db/database';

const AuthContext = createContext(null);

// `usuario` vem da sessão lembrada NESTE aparelho (SQLite local), não de
// uma chamada ao backend — isso só acontece nas telas de Login/Cadastro
// (ver LoginScreen.js/CadastroScreen.js).
export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [carregando, setCarregando] = useState(true);

  const recarregarSessao = useCallback(async () => {
    setUsuario(await obterUsuarioLogado());
  }, []);

  useEffect(() => {
    recarregarSessao().finally(() => setCarregando(false));
  }, [recarregarSessao]);

  const sair = useCallback(async () => {
    await encerrarSessao();
    await recarregarSessao();
  }, [recarregarSessao]);

  return (
    <AuthContext.Provider value={{ usuario, carregando, recarregarSessao, sair }}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
