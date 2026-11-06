import { useEffect, useRef, useState } from 'react';
import { buscarMensagens, buscarResumos, deletarResumo, salvarMensagem } from './genomicoDb';
import { perguntarAoAgente } from './api';
import { gerarNovoResumo } from './resumoService';

const NOMES_SECAO = {
  perfil: 'Seu perfil',
  ancestralidade: 'Sua ancestralidade',
  riscos_doencas: 'Riscos de doenças',
  bem_estar: 'Bem-estar e medicamentos',
  recomendacoes: 'Recomendações',
};

function formatarDataHora(iso) {
  const data = new Date(iso);
  return (
    data.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' }) +
    ' ' +
    data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  );
}

export default function Chat({ sessaoInicialId }) {
  const [subview, setSubview] = useState(sessaoInicialId ? 'conversa' : 'lista');
  const [resumos, setResumos] = useState(() => buscarResumos());
  const [sessaoAtual, setSessaoAtual] = useState(sessaoInicialId || null);
  const [mensagens, setMensagens] = useState(() => (sessaoInicialId ? buscarMensagens(sessaoInicialId) : []));
  const [texto, setTexto] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [gerando, setGerando] = useState(false);
  const [fontesAbertas, setFontesAbertas] = useState({});
  const [erro, setErro] = useState('');
  const fimDaListaRef = useRef(null);

  useEffect(() => {
    fimDaListaRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [mensagens]);

  const abrirResumo = (resumo) => {
    setSessaoAtual(resumo.sessao_id);
    setMensagens(buscarMensagens(resumo.sessao_id));
    setSubview('conversa');
  };

  const voltarParaLista = () => {
    setResumos(buscarResumos());
    setSubview('lista');
  };

  const handleNovoResumo = async () => {
    setGerando(true);
    setErro('');
    try {
      const resumo = await gerarNovoResumo();
      abrirResumo(resumo);
    } catch (e) {
      setErro(e.message);
    } finally {
      setGerando(false);
    }
  };

  const handleRemover = (resumo) => {
    if (!window.confirm('Isso vai apagar este resumo e toda a conversa associada a ele. Deseja continuar?')) return;
    deletarResumo(resumo.id, resumo.sessao_id);
    setResumos(buscarResumos());
  };

  const handleEnviar = async (evento) => {
    evento.preventDefault();
    const mensagemDigitada = texto.trim();
    if (!mensagemDigitada || !sessaoAtual) return;

    const mensagemUsuario = { id: Date.now(), autor: 'usuario', texto: mensagemDigitada };
    setMensagens((atual) => [...atual, mensagemUsuario]);
    setTexto('');
    salvarMensagem(sessaoAtual, 'usuario', mensagemDigitada);
    setEnviando(true);

    try {
      const resultado = await perguntarAoAgente(mensagemDigitada);
      const respostaIA = {
        id: Date.now() + 1,
        autor: 'ia',
        texto: resultado.answer,
        fontes: resultado.sources || [],
      };
      setMensagens((atual) => [...atual, respostaIA]);
      salvarMensagem(sessaoAtual, 'ia', resultado.answer);
    } catch (e) {
      const semRelatorio = e.message?.startsWith('Nenhum relatório enviado');
      const textoErro = semRelatorio
        ? e.message
        : `Não consegui falar com o agente agora. Verifique se o backend está rodando. Detalhe: ${e.message}`;
      const respostaErro = { id: Date.now() + 1, autor: 'ia', texto: textoErro };
      setMensagens((atual) => [...atual, respostaErro]);
      salvarMensagem(sessaoAtual, 'ia', textoErro);
    } finally {
      setEnviando(false);
    }
  };

  if (subview === 'conversa') {
    return (
      <div>
        <button type="button" className="linkVoltar" onClick={voltarParaLista}>
          ← Voltar aos resumos
        </button>

        <div className="chat-lista">
          {mensagens.map((item) => (
            <div key={item.id}>
              <div className={`chat-bolha ${item.autor === 'usuario' ? 'chat-bolha-usuario' : 'chat-bolha-ia'}`}>
                {item.texto}
              </div>

              {item.fontes?.length > 0 && (
                <div className="chat-fontes">
                  <button
                    type="button"
                    className="chat-fontes-toggle"
                    onClick={() => setFontesAbertas((atual) => ({ ...atual, [item.id]: !atual[item.id] }))}
                  >
                    {fontesAbertas[item.id] ? '▾' : '▸'} Fontes consultadas no seu relatório ({item.fontes.length})
                  </button>

                  {fontesAbertas[item.id] &&
                    item.fontes.map((fonte, indice) => (
                      <p key={indice} className="chat-fonte-item">
                        <strong>{NOMES_SECAO[fonte.section] || fonte.section}: </strong>
                        {fonte.text.length > 180 ? `${fonte.text.slice(0, 180)}…` : fonte.text}
                      </p>
                    ))}
                </div>
              )}
            </div>
          ))}
          <div ref={fimDaListaRef} />
        </div>

        <form className="chat-input-row" onSubmit={handleEnviar}>
          <textarea
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Digite sua pergunta..."
            disabled={enviando}
            rows={2}
          />
          <button type="submit" className="primario" disabled={enviando || !texto.trim()}>
            {enviando ? 'Enviando...' : 'Enviar'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div>
      <div className="botoes">
        <button type="button" className="primario" onClick={handleNovoResumo} disabled={gerando}>
          {gerando ? 'Gerando...' : '+ Novo Resumo'}
        </button>
      </div>

      {erro && <p className="erro" role="alert">{erro}</p>}

      {resumos.length === 0 ? (
        <p className="introducao">Nenhum resumo ainda. Clique em "+ Novo Resumo" para gerar o primeiro.</p>
      ) : (
        resumos.map((resumo) => (
          <div key={resumo.id} className="resumo-card" onClick={() => abrirResumo(resumo)}>
            <div className="resumo-card-info">
              <span className="resumo-card-data">{formatarDataHora(resumo.data_criacao)}</span>
              <p>
                {resumo.conteudo.slice(0, 140)}
                {resumo.conteudo.length > 140 ? '…' : ''}
              </p>
            </div>
            <button
              type="button"
              className="resumo-card-remover"
              onClick={(evento) => {
                evento.stopPropagation();
                handleRemover(resumo);
              }}
            >
              🗑️
            </button>
          </div>
        ))
      )}
    </div>
  );
}
