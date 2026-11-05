import { useState } from 'react';
import Auth from './Auth';
import Dashboard from './Dashboard';
import * as sessao from './sessao';

/**
 * Componente raiz: mostra a tela de autenticação ou o dashboard, conforme a sessão.
 */
export default function App() {
  const [usuario, setUsuario] = useState(() => sessao.obter());

  /**
   * Encerra a sessão do usuário atual.
   */
  const handleSair = () => {
    sessao.limpar();
    setUsuario(null);
  };

  if (!usuario) {
    return <Auth onAutenticado={setUsuario} />;
  }

  return <Dashboard usuario={usuario} onSair={handleSair} />;
}
