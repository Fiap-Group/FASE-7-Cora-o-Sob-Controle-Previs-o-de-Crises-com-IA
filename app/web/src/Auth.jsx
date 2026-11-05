import { useState } from 'react';
import { cadastrar, definirNickname, login } from './api';
import { salvar } from './sessao';

const REGEX_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function Auth({ onAutenticado }) {
  const [modo, setModo] = useState('login'); // 'login' | 'cadastro' | 'nickname'
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [nickname, setNickname] = useState('');
  const [usuarioId, setUsuarioId] = useState(null);
  const [erro, setErro] = useState('');
  const [enviando, setEnviando] = useState(false);

  const emailValido = REGEX_EMAIL.test(email.trim());

  const handleLogin = async (evento) => {
    evento.preventDefault();
    setErro('');
    setEnviando(true);
    try {
      const usuario = await login(email.trim(), senha);
      salvar(usuario);
      onAutenticado(usuario);
    } catch (e) {
      setErro(e.message);
    } finally {
      setEnviando(false);
    }
  };

  const handleCadastro = async (evento) => {
    evento.preventDefault();
    setErro('');
    if (!emailValido) {
      setErro('E-mail inválido.');
      return;
    }

    setEnviando(true);
    try {
      const usuario = await cadastrar(email.trim(), senha);
      setUsuarioId(usuario.id);
      setModo('nickname');
    } catch (e) {
      setErro(e.message);
    } finally {
      setEnviando(false);
    }
  };

  const handleNickname = async (evento) => {
    evento.preventDefault();
    setErro('');
    if (!nickname.trim()) {
      setErro('Escolha um nickname.');
      return;
    }

    setEnviando(true);
    try {
      const usuario = await definirNickname(usuarioId, nickname.trim());
      salvar(usuario);
      onAutenticado(usuario);
    } catch (e) {
      setErro(e.message);
    } finally {
      setEnviando(false);
    }
  };

  if (modo === 'nickname') {
    return (
      <main className="container">
        <h1>Quase lá!</h1>
        <p className="introducao">Escolha um nickname para a sua conta.</p>
        <form className="formulario" onSubmit={handleNickname}>
          <label className="campo">
            <span>Nickname</span>
            <input
              type="text"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              placeholder="Como quer ser chamado?"
              disabled={enviando}
              autoFocus
            />
          </label>
          <div className="botoes">
            <button type="submit" className="primario" disabled={enviando}>
              {enviando ? 'Salvando...' : 'Concluir cadastro'}
            </button>
          </div>
        </form>
        {erro && <p className="erro">{erro}</p>}
      </main>
    );
  }

  const ehLogin = modo === 'login';

  return (
    <main className="container">
      <h1>CardioIA</h1>
      <p className="introducao">
        {ehLogin ? 'Entre com sua conta para acompanhar os indicadores de risco.' : 'Cadastre-se para começar.'}
      </p>

      <form className="formulario" onSubmit={ehLogin ? handleLogin : handleCadastro}>
        <label className="campo">
          <span>E-mail</span>
          <input
            type="text"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="voce@exemplo.com"
            disabled={enviando}
          />
          {!ehLogin && email.trim().length > 0 && !emailValido && <span className="erroCampo">E-mail inválido</span>}
        </label>

        <label className="campo">
          <span>Senha</span>
          <input
            type="password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            placeholder="••••••••"
            disabled={enviando}
          />
        </label>

        <div className="botoes">
          <button type="submit" className="primario" disabled={enviando || (!ehLogin && !emailValido)}>
            {enviando ? 'Enviando...' : ehLogin ? 'Entrar' : 'Criar conta'}
          </button>
        </div>
      </form>

      {erro && <p className="erro">{erro}</p>}

      <button type="button" className="linkAlternar" onClick={() => setModo(ehLogin ? 'cadastro' : 'login')}>
        {ehLogin ? 'Não tem conta? Cadastre-se' : 'Já tem conta? Entrar'}
      </button>
    </main>
  );
}
