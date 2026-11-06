import { useMemo, useState } from 'react';
import { View, Text, ScrollView, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { GRUPOS_RISCO_CARDIACO, RISCO_CARDIACO_FEATURES } from '../data/riscoCardiacoFeatures';
import { avaliarRisco } from '../services/riscoService';
import { buscarLeituraIot } from '../services/api';
import { avisar } from '../utils/alerta';
import { useAuth } from '../context/AuthContext';
import { useTema } from '../theme/ThemeContext';
import criarEstilos from '../styles/ancestralidadeScreenStyles';

const VALORES_INICIAIS = Object.fromEntries(RISCO_CARDIACO_FEATURES.map((f) => [f.chave, '']));
const VALORES_EXEMPLO = Object.fromEntries(RISCO_CARDIACO_FEATURES.map((f) => [f.chave, String(f.exemplo)]));

/** Tela de formulário para informar métricas e solicitar a avaliação de risco cardíaco. */
export default function PrevisaoFormScreen({ navigation }) {
  const { usuario } = useAuth();
  const { colors } = useTema();
  const styles = useMemo(() => criarEstilos(colors), [colors]);
  const [valores, setValores] = useState(VALORES_INICIAIS);
  const [enviando, setEnviando] = useState(false);
  const [buscandoIot, setBuscandoIot] = useState(false);

  /** Atualiza o valor digitado para um campo do formulário. */
  const atualizarCampo = (chave, texto) => {
    setValores((atual) => ({ ...atual, [chave]: texto }));
  };

  /** Preenche o formulário com valores de exemplo. */
  const handleUsarExemplo = () => {
    setValores(VALORES_EXEMPLO);
  };

  /** Busca a leitura atual do sensor IoT e preenche os campos correspondentes do formulário. */
  const handleUsarLeituraIot = async () => {
    setBuscandoIot(true);
    try {
      const leitura = await buscarLeituraIot();
      const semLeitura =
        !leitura.conectado || leitura.fc_media == null || leitura.pa_sistolica == null || leitura.spo2_media == null;

      if (semLeitura) {
        avisar(
          'Sensor sem leitura ainda',
          'O ESP32 ainda não publicou nenhuma leitura. Verifique se a simulação no Wokwi está rodando e conectada ao broker MQTT.'
        );
        return;
      }

      setValores((atual) => ({
        ...atual,
        fc_media: String(leitura.fc_media),
        pa_sistolica: String(leitura.pa_sistolica),
        spo2_media: String(leitura.spo2_media),
      }));
    } catch (erro) {
      avisar('Não foi possível buscar a leitura do sensor', erro.message);
    } finally {
      setBuscandoIot(false);
    }
  };

  /** Valida e monta o payload numérico do formulário para envio à avaliação de risco. */
  const montarPayload = () => {
    const payload = {};
    for (const { chave, label } of RISCO_CARDIACO_FEATURES) {
      const numero = Number(String(valores[chave]).replace(',', '.'));
      if (valores[chave].trim() === '' || Number.isNaN(numero)) {
        avisar('Campo inválido', `Informe um número válido para "${label}".`);
        return null;
      }
      payload[chave] = numero;
    }
    return payload;
  };

  /** Monta o payload, solicita a avaliação de risco e navega para o resultado. */
  const handleAvaliar = async () => {
    const payload = montarPayload();
    if (!payload) return;

    setEnviando(true);
    try {
      const resultado = await avaliarRisco(payload, usuario?.id);
      navigation.navigate('PrevisaoResultado', { resultado });
    } catch (erro) {
      avisar(
        'Não foi possível avaliar o risco',
        `Verifique se o backend está rodando e se a chave de API foi configurada.\n\n${erro.message}`
      );
    } finally {
      setEnviando(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.sectionTitle}>Previsão de Risco Cardíaco</Text>
        <Text style={styles.introducao}>
          Informe as métricas atuais de operação para que o sistema multiagente avalie o risco de uma crise e
          sugira os protocolos de resposta aplicáveis.
        </Text>

        <View style={styles.formulario}>
          {GRUPOS_RISCO_CARDIACO.map(({ chave: grupoChave, titulo }) => (
            <View key={grupoChave}>
              <Text style={styles.subtituloFormulario}>{titulo}</Text>
              {RISCO_CARDIACO_FEATURES.filter((f) => f.grupo === grupoChave).map(({ chave, label, unidade }) => (
                <View key={chave} style={styles.campo}>
                  <Text style={styles.label}>
                    {label} ({unidade})
                  </Text>
                  <TextInput
                    style={styles.inputTexto}
                    value={valores[chave]}
                    onChangeText={(texto) => atualizarCampo(chave, texto)}
                    placeholder="0"
                    keyboardType="numeric"
                    editable={!enviando}
                  />
                </View>
              ))}
            </View>
          ))}

          <View style={styles.botoesLinha}>
            <TouchableOpacity
              style={styles.botaoSecundario}
              onPress={handleUsarLeituraIot}
              disabled={enviando || buscandoIot}
            >
              <Text style={styles.botaoSecundarioTexto}>
                {buscandoIot ? 'Buscando...' : 'Usar leitura do sensor (IoT)'}
              </Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.botaoSecundario} onPress={handleUsarExemplo} disabled={enviando}>
              <Text style={styles.botaoSecundarioTexto}>Usar exemplo</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.botaoPrimario, enviando && styles.botaoDesabilitado]}
              onPress={handleAvaliar}
              disabled={enviando}
            >
              <Text style={styles.botaoPrimarioTexto}>{enviando ? 'Avaliando...' : 'Avaliar risco'}</Text>
            </TouchableOpacity>
          </View>

          {enviando && (
            <View style={styles.avisoEnviando}>
              <ActivityIndicator color={colors.primary} />
              <Text style={styles.avisoEnviandoTexto}>
                A cadeia de agentes de IA está analisando os dados — isso pode levar até um minuto.
              </Text>
            </View>
          )}
        </View>
      </View>
    </ScrollView>
  );
}
