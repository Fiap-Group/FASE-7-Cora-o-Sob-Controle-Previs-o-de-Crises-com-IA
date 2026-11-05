import { useEffect, useState } from 'react';
import { RISCO_CARDIACO_FEATURES } from './riscoCardiacoFeatures';
import { buscarPerfil } from './api';

const NIVEL_POR_CLASSIFICACAO = {
  'Alto risco': 'alto',
  'Baixo risco': 'baixo',
};

const PALETA_CORES = ['#2a78d6', '#d6762a', '#2ad6a0', '#a02ad6', '#d62a5e', '#5e9e2a'];

/**
 * Escolhe uma cor de avatar com base no id do usuário.
 */
function corAvatar(usuarioId) {
  return PALETA_CORES[(usuarioId ?? 0) % PALETA_CORES.length];
}

/**
 * Formata uma data ISO em data e hora no padrão brasileiro.
 */
function formatarDataHora(iso) {
  const data = new Date(iso);
  return (
    data.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' }) +
    ' ' +
    data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  );
}

/**
 * Exibe o perfil do usuário: avaliação de risco mais recente, dados e histórico.
 */
export default function Perfil({ usuario }) {
  const [perfil, setPerfil] = useState(null);
  const [erro, setErro] = useState('');
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    let cancelado = false;
    setCarregando(true);
    setErro('');
    buscarPerfil(usuario.id)
      .then((resposta) => {
        if (!cancelado) setPerfil(resposta);
      })
      .catch((e) => {
        if (!cancelado) setErro(e.message);
      })
      .finally(() => {
        if (!cancelado) setCarregando(false);
      });
    return () => {
      cancelado = true;
    };
  }, [usuario.id]);

  if (carregando && !perfil) return <p className="introducao">Carregando perfil...</p>;
  if (erro) return <p className="erro">{erro}</p>;

  const avaliacao = perfil?.avaliacao_mais_recente;

  return (
    <div>
      <div className="perfil-cabecalho">
        <div className="avatar-circulo" style={{ backgroundColor: corAvatar(usuario.id) }}>
          {(usuario.nickname || '?').trim().charAt(0).toUpperCase()}
        </div>
        <h2>{usuario.nickname}</h2>
        <p className="introducao">{usuario.email}</p>
      </div>

      <h3>Risco mais recente</h3>
      {avaliacao ? (
        <section className="resultado">
          <h2>
            Risco de crise cardíaca ({Math.round(avaliacao.probabilidade * 100)}%) —{' '}
            <span className={`nivel-${NIVEL_POR_CLASSIFICACAO[avaliacao.classificacao] ?? 'moderado'}`}>
              {avaliacao.classificacao}
            </span>
          </h2>
          <p>{avaliacao.recomendacao}</p>
        </section>
      ) : (
        <p className="introducao">Nenhuma avaliação ainda. Use a aba "Avaliar risco" para gerar a primeira.</p>
      )}

      {avaliacao && (
        <>
          <h3>Dados dessa avaliação</h3>
          <div className="perfil-grid">
            {RISCO_CARDIACO_FEATURES.map(({ chave, label, unidade }) => (
              <div key={chave} className="perfil-chip">
                <span className="perfil-chip-label">{label}</span>
                <span className="perfil-chip-valor">
                  {avaliacao.dados[chave]} {unidade}
                </span>
              </div>
            ))}
          </div>
        </>
      )}

      {perfil?.historico?.length > 0 && (
        <>
          <h3>Histórico</h3>
          <div className="historico">
            {perfil.historico.map((item) => (
              <div key={item.criado_em} className="historico-item">
                <span>{formatarDataHora(item.criado_em)}</span>
                <span className={`historico-badge nivel-${NIVEL_POR_CLASSIFICACAO[item.classificacao] ?? 'moderado'}`}>
                  {item.classificacao}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
