import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { encerrarSessao, obterUsuarioLogado } from '../db/database';

const AuthContext = createContext(null);

/** Provedor de contexto que mantém o usuário logado e expõe ações de sessão. */
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

/** Hook de acesso ao contexto de autenticação. */
export function useAuth() {
  return useContext(AuthContext);
}
