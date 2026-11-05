import { useState } from 'react';
import { RISCO_CARDIACO_FEATURES } from './riscoCardiacoFeatures';
import { avaliarRiscoCardiaco, buscarLeituraIot } from './api';
import Perfil from './Perfil';

const VALORES_INICIAIS = Object.fromEntries(RISCO_CARDIACO_FEATURES.map((f) => [f.chave, '']));
const VALORES_EXEMPLO = Object.fromEntries(RISCO_CARDIACO_FEATURES.map((f) => [f.chave, String(f.exemplo)]));

const NIVEL_POR_CLASSIFICACAO = {
  'Alto risco': 'alto',
  'Baixo risco': 'baixo',
};

/**
 * Dashboard principal: avalia o risco cardíaco a partir das métricas informadas e exibe o perfil do usuário.
 */
export default function Dashboard({ usuario, onSair }) {
  const [aba, setAba] = useState('avaliar');
  const [valores, setValores] = useState(VALORES_INICIAIS);
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState('');
  const [avaliando, setAvaliando] = useState(false);
  const [buscandoIot, setBuscandoIot] = useState(false);

  /**
   * Atualiza o valor digitado em um campo do formulário.
   */
  const atualizarCampo = (chave, texto) => {
    setValores((atual) => ({ ...atual, [chave]: texto }));
  };

  /**
   * Preenche o formulário com os valores de exemplo.
   */
  const handleUsarExemplo = () => setValores(VALORES_EXEMPLO);

  /**
   * Busca a leitura do sensor IoT e preenche as métricas vitais no formulário.
   */
  const handleUsarLeituraIot = async () => {
    setBuscandoIot(true);
    setErro('');
    try {
      const leitura = await buscarLeituraIot();
      const semLeitura =
        !leitura.conectado || leitura.fc_media == null || leitura.pa_sistolica == null || leitura.spo2_media == null;

      if (semLeitura) {
        setErro('O ESP32 ainda não publicou nenhuma leitura. Verifique a simulação no Wokwi e o broker MQTT.');
        return;
      }

      setValores({
        ...VALORES_EXEMPLO,
        fc_media: String(leitura.fc_media),
        pa_sistolica: String(leitura.pa_sistolica),
        spo2_media: String(leitura.spo2_media),
      });
    } catch (e) {
      setErro(e.message);
    } finally {
      setBuscandoIot(false);
    }
  };

  /**
   * Valida e converte os valores do formulário em um payload numérico para a avaliação.
   */
  const montarPayload = () => {
    const payload = {};
    for (const { chave, label } of RISCO_CARDIACO_FEATURES) {
      const numero = Number(String(valores[chave]).replace(',', '.'));
      if (valores[chave].trim() === '' || Number.isNaN(numero)) {
        setErro(`Informe um número válido para "${label}".`);
        return null;
      }
      payload[chave] = numero;
    }
    return payload;
  };

  /**
   * Envia o payload para avaliação do risco cardíaco e exibe o resultado.
   */
  const handleAvaliar = async (evento) => {
    evento.preventDefault();
    setErro('');
    const payload = montarPayload();
    if (!payload) return;

    setAvaliando(true);
    setResultado(null);
    try {
      const resposta = await avaliarRiscoCardiaco(payload, usuario.id);
      setResultado(resposta);
    } catch (e) {
      setErro(e.message);
    } finally {
      setAvaliando(false);
    }
  };

  return (
    <main className="container">
      <div className="cabecalho">
        <h1>CardioIA</h1>
        <button type="button" className="linkSair" onClick={onSair}>
          Olá, {usuario.nickname} — Sair
        </button>
      </div>
      <div className="botoes-aba">
        <button type="button" className={aba === 'avaliar' ? 'primario' : ''} onClick={() => setAba('avaliar')}>
          Avaliar risco
        </button>
        <button type="button" className={aba === 'perfil' ? 'primario' : ''} onClick={() => setAba('perfil')}>
          Perfil
        </button>
      </div>

      {aba === 'perfil' && <Perfil usuario={usuario} />}

      {aba === 'avaliar' && (
        <>
          <p className="introducao">
            Informe as métricas atuais de operação para que o sistema multiagente avalie o risco de uma crise
            cardíaca e sugira os protocolos de resposta aplicáveis.
          </p>

          <form className="formulario" onSubmit={handleAvaliar}>
            {RISCO_CARDIACO_FEATURES.map(({ chave, label, unidade }) => (
              <label key={chave} className="campo">
                <span>
                  {label} ({unidade})
                </span>
                <input
                  type="text"
                  inputMode="decimal"
                  value={valores[chave]}
                  onChange={(e) => atualizarCampo(chave, e.target.value)}
                  placeholder="0"
                  disabled={avaliando}
                />
              </label>
            ))}

            <div className="botoes">
              <button type="button" onClick={handleUsarLeituraIot} disabled={avaliando || buscandoIot}>
                {buscandoIot ? 'Buscando...' : 'Buscar leitura do sensor (IoT)'}
              </button>
              <button type="button" onClick={handleUsarExemplo} disabled={avaliando}>
                Usar exemplo
              </button>
              <button type="submit" className="primario" disabled={avaliando}>
                {avaliando ? 'Avaliando...' : 'Avaliar risco'}
              </button>
            </div>
          </form>

          {erro && <p className="erro">{erro}</p>}

          {resultado && (
            <section className="resultado">
              <h2>
                Risco de crise cardíaca ({Math.round(resultado.probabilidade * 100)}%) —{' '}
                <span className={`nivel-${NIVEL_POR_CLASSIFICACAO[resultado.classificacao] ?? 'moderado'}`}>
                  {resultado.classificacao}
                </span>
              </h2>
              <p>{resultado.recomendacao}</p>

              <h3>Protocolos sugeridos</h3>
              <ul>
                {resultado.protocolos.map((protocolo) => (
                  <li key={protocolo}>{protocolo}</li>
                ))}
              </ul>

              <p className="disclaimer">
                Esta recomendação foi gerada por um sistema de IA a partir de dados sintéticos de operação. Use-a
                como apoio, não como decisão clínica final.
              </p>
            </section>
          )}
        </>
      )}
    </main>
  );
}
