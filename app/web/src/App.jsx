import { useState } from 'react';
import Auth from './Auth';
import Dashboard from './Dashboard';
import * as sessao from './sessao';

// A conta mora no backend (src/modules/auth) e é compartilhada com o app
// mobile — sem sessão lembrada neste navegador, só o fluxo de
// Login/Cadastro aparece; o dashboard só depois de autenticado.
export default function App() {
  const [usuario, setUsuario] = useState(() => sessao.obter());

  const handleSair = () => {
    sessao.limpar();
    setUsuario(null);
  };

  if (!usuario) {
    return <Auth onAutenticado={setUsuario} />;
  }

  return <Dashboard usuario={usuario} onSair={handleSair} />;
}
