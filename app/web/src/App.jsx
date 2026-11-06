import { useEffect, useState } from 'react';
import Auth from './Auth';
import Dashboard from './Dashboard';
import * as sessao from './sessao';
import { aplicarTema, obterTemaInicial, salvarTema } from './tema';

export default function App() {
  const [usuario, setUsuario] = useState(() => sessao.obter());
  const [tema, setTema] = useState(obterTemaInicial);

  useEffect(() => {
    aplicarTema(tema);
    salvarTema(tema);
  }, [tema]);

  const alternarTema = () => setTema((atual) => (atual === 'dark' ? 'light' : 'dark'));

  const handleSair = () => {
    sessao.limpar();
    setUsuario(null);
  };

  if (!usuario) {
    return <Auth onAutenticado={setUsuario} />;
  }

  return <Dashboard usuario={usuario} onSair={handleSair} tema={tema} onAlternarTema={alternarTema} />;
}
