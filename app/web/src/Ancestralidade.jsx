import { useRef, useState } from 'react';
import {
  buscarPerfilGenomicoAtual,
  registrarConsentimento,
  salvarPerfilGenomico,
  temConsentimento,
  apagarDadosGenomicos,
} from './genomicoDb';
import { apagarIndiceNoBackend, indexarRelatorio } from './api';
import { gerarNovoResumo } from './resumoService';
import { mapearAncestralidade, mapearNivelRisco, mapearRiscos } from './perfilGenomico';
import relatorioGenomicoExemplo from './relatorioGenomicoExemplo';
import Chat from './Chat';

const OPCOES_SEXO = [
  { label: 'Prefiro não informar', value: 'nao_informado' },
  { label: 'Feminino', value: 'feminino' },
  { label: 'Masculino', value: 'masculino' },
];

const OPCOES_NIVEL_RISCO = [
  { label: 'Baixo', value: 'baixo' },
  { label: 'Moderado', value: 'moderado' },
  { label: 'Alto', value: 'alto' },
  { label: 'Muito alto', value: 'muito alto' },
];

/**
 * Seção de ancestralidade/relatório genômico: envio do relatório, visão do perfil (barras de
 * ancestralidade + riscos de doenças) e acesso às conversas/resumos gerados pelo agente de IA.
 */
export default function Ancestralidade() {
  const perfilInicial = buscarPerfilGenomicoAtual();
  const [perfil, setPerfil] = useState(perfilInicial);
  const [visao, setVisao] = useState(perfilInicial ? 'perfil' : 'formulario');
  const [sessaoParaAbrir, setSessaoParaAbrir] = useState(null);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState('');

  const [pacienteNome, setPacienteNome] = useState('');
  const [pacienteDataNascimento, setPacienteDataNascimento] = useState('');
  const [pacienteSexo, setPacienteSexo] = useState('nao_informado');
  const [ancestralidadeLinhas, setAncestralidadeLinhas] = useState([{ id: 'anc-0', origem: '', percentual: '' }]);
  const [riscosLinhas, setRiscosLinhas] = useState([{ id: 'risco-0', nome: '', nivel: 'moderado', descricao: '' }]);

  const contadorId = useRef(1);
  /** Gera um id sequencial único para uma nova linha do formulário. */
  const novoId = (prefixo) => `${prefixo}-${contadorId.current++}`;

  /** Preenche os campos do formulário a partir de um relatório genômico existente. */
  const preencherFormularioComPerfil = (dados) => {
    if (!dados) return;
    setPacienteNome(dados.paciente?.nome || '');
    setPacienteDataNascimento(dados.paciente?.data_nascimento || '');
    setPacienteSexo(dados.paciente?.sexo || 'nao_informado');
    setAncestralidadeLinhas(
      (dados.ancestralidade?.composicao || []).map((item) => ({
        id: novoId('anc'),
        origem: item.origem || '',
        percentual: item.percentual != null ? String(item.percentual) : '',
      }))
    );
    setRiscosLinhas(
      (dados.riscos_doencas || []).map((item) => ({
        id: novoId('risco'),
        nome: item.nome || '',
        nivel: mapearNivelRisco(item.nivel_risco),
        descricao: item.descricao || '',
      }))
    );
  };

  /** Preenche o formulário com um relatório genômico de exemplo. */
  const handleUsarExemplo = () => preencherFormularioComPerfil(relatorioGenomicoExemplo);

  /** Abre o formulário preenchido com o relatório atual, para edição/substituição. */
  const handleAbrirNovoRelatorio = () => {
    preencherFormularioComPerfil(perfil);
    setSessaoParaAbrir(null);
    setVisao('formulario');
  };

  const atualizarAncestralidadeLinha = (id, campo, valor) =>
    setAncestralidadeLinhas((atual) => atual.map((l) => (l.id === id ? { ...l, [campo]: valor } : l)));
  const adicionarAncestralidadeLinha = () =>
    setAncestralidadeLinhas((atual) => [...atual, { id: novoId('anc'), origem: '', percentual: '' }]);
  const removerAncestralidadeLinha = (id) =>
    setAncestralidadeLinhas((atual) => atual.filter((l) => l.id !== id));

  const atualizarRiscoLinha = (id, campo, valor) =>
    setRiscosLinhas((atual) => atual.map((l) => (l.id === id ? { ...l, [campo]: valor } : l)));
  const adicionarRiscoLinha = () =>
    setRiscosLinhas((atual) => [...atual, { id: novoId('risco'), nome: '', nivel: 'moderado', descricao: '' }]);
  const removerRiscoLinha = (id) => setRiscosLinhas((atual) => atual.filter((l) => l.id !== id));

  /** Monta o relatório genômico a partir dos dados preenchidos no formulário, descartando linhas vazias. */
  const montarRelatorio = () => {
    const ancestralidadeValida = ancestralidadeLinhas
      .map((l) => ({ origem: l.origem.trim(), percentual: Number(String(l.percentual).replace(',', '.')) }))
      .filter((l) => l.origem && !Number.isNaN(l.percentual));

    const riscosValidos = riscosLinhas
      .map((l) => ({ nome: l.nome.trim(), nivel_risco: l.nivel, descricao: l.descricao.trim() }))
      .filter((l) => l.nome);

    return {
      paciente: {
        id: `PAC-${Date.now()}`,
        nome: pacienteNome.trim(),
        data_nascimento: pacienteDataNascimento.trim(),
        sexo: pacienteSexo,
        data_exame: new Date().toLocaleDateString('pt-BR'),
        laboratorio: 'Laboratório Parceiro',
      },
      ancestralidade: { composicao: ancestralidadeValida },
      riscos_doencas: riscosValidos,
      bem_estar: {},
      recomendacoes: {},
    };
  };

  /** Indexa o relatório no backend, salva localmente e gera o primeiro resumo automático. */
  const enviarRelatorio = async (perfilMontado) => {
    setEnviando(true);
    setErro('');
    try {
      await indexarRelatorio(perfilMontado);
      salvarPerfilGenomico(perfilMontado);
      setPerfil(perfilMontado);
      setVisao('perfil');

      try {
        const resumo = await gerarNovoResumo();
        setSessaoParaAbrir(resumo.sessao_id);
        setVisao('chat');
      } catch (erroResumo) {
        setErro(
          'Seu relatório foi salvo, mas a geração do primeiro resumo falhou. Verifique se o backend está ' +
            `rodando e se a chave de API foi configurada. Você pode gerar um resumo depois na aba "Conversas".\n\n${erroResumo.message}`
        );
      }
    } catch (erro) {
      setErro(erro.message);
    } finally {
      setEnviando(false);
    }
  };

  /** Valida o formulário e, após confirmar o consentimento quando necessário, envia o relatório. */
  const handleEnviar = async (evento) => {
    evento.preventDefault();
    setErro('');

    if (!pacienteNome.trim()) {
      setErro('Informe seu nome antes de enviar.');
      return;
    }

    const perfilMontado = montarRelatorio();
    if (perfilMontado.ancestralidade.composicao.length === 0) {
      setErro('Adicione ao menos uma região de ancestralidade com percentual válido.');
      return;
    }

    if (temConsentimento()) {
      await enviarRelatorio(perfilMontado);
      return;
    }

    const autorizou = window.confirm(
      'Autorização para usar seus dados\n\n' +
        'Seu relatório tem informações genéticas (dados de saúde). Elas serão usadas só para explicar o ' +
        'seu relatório. Parte do texto é enviada ao serviço de IA do Google, sem seu nome e sem sua data ' +
        'de nascimento. Você pode apagar tudo depois, quando quiser. Você autoriza?'
    );
    if (!autorizou) return;

    registrarConsentimento();
    await enviarRelatorio(perfilMontado);
  };

  /** Confirma e apaga todos os dados genômicos, no navegador e no índice do backend. */
  const handleApagarDados = async () => {
    if (
      !window.confirm(
        'Isso remove deste navegador o relatório, o histórico de conversas e os resumos, e apaga o índice ' +
          'do backend. Não dá para desfazer.'
      )
    )
      return;

    await apagarIndiceNoBackend();
    apagarDadosGenomicos();
    setPerfil(null);
    setSessaoParaAbrir(null);
    setVisao('formulario');
  };

  const ancestralidadeMapeada = mapearAncestralidade(perfil);
  const riscosMapeados = mapearRiscos(perfil);

  return (
    <div>
      {perfil && (
        <div className="botoes-aba botoes-aba-secundaria">
          <button
            type="button"
            className={visao === 'perfil' ? 'primario' : ''}
            onClick={() => {
              setSessaoParaAbrir(null);
              setVisao('perfil');
            }}
          >
            Perfil genômico
          </button>
          <button
            type="button"
            className={visao === 'chat' ? 'primario' : ''}
            onClick={() => {
              setSessaoParaAbrir(null);
              setVisao('chat');
            }}
          >
            Conversas
          </button>
        </div>
      )}

      {erro && <p className="erro">{erro}</p>}

      {visao === 'chat' && <Chat sessaoInicialId={sessaoParaAbrir} />}

      {visao === 'perfil' && perfil && (
        <>
          <p className="introducao">
            Estimativa da composição da sua ancestralidade e dos riscos de doenças, com base nas variantes
            analisadas no seu relatório de DNA.
          </p>

          <h3>Ancestralidade</h3>
          {ancestralidadeMapeada.map((item) => (
            <div key={item.regiao} className="ancestralidade-barra">
              <div className="ancestralidade-barra-linha">
                <span>{item.regiao}</span>
                <strong>{item.percentual}%</strong>
              </div>
              <div className="ancestralidade-barra-trilha">
                <div className="ancestralidade-barra-progresso" style={{ width: `${item.percentual}%` }} />
              </div>
            </div>
          ))}

          {riscosMapeados.length > 0 && (
            <>
              <h3>Riscos de doenças</h3>
              {riscosMapeados.map((risco) => (
                <div key={risco.id} className="resultado">
                  <h4>
                    {risco.condicao} —{' '}
                    <span className={`nivel-${risco.nivel.replace(' ', '-')}`}>{risco.nivel}</span>
                  </h4>
                  {risco.descricao && <p>{risco.descricao}</p>}
                </div>
              ))}
            </>
          )}

          <div className="botoes">
            <button type="button" onClick={handleAbrirNovoRelatorio}>
              Enviar novo relatório
            </button>
            <button type="button" onClick={handleApagarDados}>
              Apagar meus dados
            </button>
          </div>
        </>
      )}

      {visao === 'formulario' && (
        <form className="formulario" onSubmit={handleEnviar}>
          <h3>Enviar relatório genômico</h3>

          {perfil && (
            <button type="button" className="linkVoltar" onClick={() => setVisao('perfil')} disabled={enviando}>
              ← Cancelar e voltar ao perfil
            </button>
          )}

          <label className="campo">
            <span>Nome</span>
            <input type="text" value={pacienteNome} onChange={(e) => setPacienteNome(e.target.value)} disabled={enviando} />
          </label>

          <label className="campo">
            <span>Data de nascimento</span>
            <input
              type="text"
              value={pacienteDataNascimento}
              onChange={(e) => setPacienteDataNascimento(e.target.value)}
              placeholder="DD/MM/AAAA"
              disabled={enviando}
            />
          </label>

          <label className="campo">
            <span>Sexo</span>
            <select value={pacienteSexo} onChange={(e) => setPacienteSexo(e.target.value)} disabled={enviando}>
              {OPCOES_SEXO.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>

          <h4>Ancestralidade</h4>
          {ancestralidadeLinhas.map((linha) => (
            <div key={linha.id} className="linha-dinamica">
              <input
                type="text"
                value={linha.origem}
                onChange={(e) => atualizarAncestralidadeLinha(linha.id, 'origem', e.target.value)}
                placeholder="Ex: Europa Ibérica"
                disabled={enviando}
              />
              <input
                type="text"
                inputMode="decimal"
                value={linha.percentual}
                onChange={(e) => atualizarAncestralidadeLinha(linha.id, 'percentual', e.target.value)}
                placeholder="%"
                disabled={enviando}
              />
              <button type="button" className="botao-remover-linha" onClick={() => removerAncestralidadeLinha(linha.id)} disabled={enviando}>
                ×
              </button>
            </div>
          ))}
          <button type="button" onClick={adicionarAncestralidadeLinha} disabled={enviando}>
            + Adicionar região
          </button>

          <h4>Riscos de doenças</h4>
          {riscosLinhas.map((linha) => (
            <div key={linha.id} className="bloco-risco">
              <label className="campo">
                <span>Condição</span>
                <input
                  type="text"
                  value={linha.nome}
                  onChange={(e) => atualizarRiscoLinha(linha.id, 'nome', e.target.value)}
                  placeholder="Ex: Diabetes Tipo 2"
                  disabled={enviando}
                />
              </label>
              <label className="campo">
                <span>Nível de risco</span>
                <select
                  value={linha.nivel}
                  onChange={(e) => atualizarRiscoLinha(linha.id, 'nivel', e.target.value)}
                  disabled={enviando}
                >
                  {OPCOES_NIVEL_RISCO.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="campo">
                <span>Descrição (opcional)</span>
                <textarea
                  value={linha.descricao}
                  onChange={(e) => atualizarRiscoLinha(linha.id, 'descricao', e.target.value)}
                  placeholder="Detalhes do resultado, variantes, recomendações..."
                  rows={2}
                  disabled={enviando}
                />
              </label>
              <button type="button" onClick={() => removerRiscoLinha(linha.id)} disabled={enviando}>
                Remover
              </button>
            </div>
          ))}
          <button type="button" onClick={adicionarRiscoLinha} disabled={enviando}>
            + Adicionar risco
          </button>

          <div className="botoes">
            <button type="button" onClick={handleUsarExemplo} disabled={enviando}>
              Usar exemplo
            </button>
            <button type="submit" className="primario" disabled={enviando}>
              {enviando ? 'Enviando...' : 'Enviar relatório'}
            </button>
          </div>
        </form>
      )}

      <p className="disclaimer">
        Isto é uma informação, não um diagnóstico. Converse com seu médico antes de tomar qualquer decisão.
      </p>
    </div>
  );
}
