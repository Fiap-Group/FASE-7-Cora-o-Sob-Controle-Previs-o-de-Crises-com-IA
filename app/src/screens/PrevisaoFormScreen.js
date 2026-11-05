import { useState } from 'react';
import { View, Text, ScrollView, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { RISCO_CARDIACO_FEATURES } from '../data/riscoCardiacoFeatures';
import { avaliarRisco } from '../services/riscoService';
import { avisar } from '../utils/alerta';
import { colors } from '../theme/colors';
import styles from '../styles/ancestralidadeScreenStyles';

const VALORES_INICIAIS = Object.fromEntries(RISCO_CARDIACO_FEATURES.map((f) => [f.chave, '']));
const VALORES_EXEMPLO = Object.fromEntries(RISCO_CARDIACO_FEATURES.map((f) => [f.chave, String(f.exemplo)]));

export default function PrevisaoFormScreen({ navigation }) {
  const [valores, setValores] = useState(VALORES_INICIAIS);
  const [enviando, setEnviando] = useState(false);

  const atualizarCampo = (chave, texto) => {
    setValores((atual) => ({ ...atual, [chave]: texto }));
  };

  const handleUsarExemplo = () => {
    setValores(VALORES_EXEMPLO);
  };

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

  const handleAvaliar = async () => {
    const payload = montarPayload();
    if (!payload) return;

    setEnviando(true);
    try {
      const resultado = await avaliarRisco(payload);
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
          {RISCO_CARDIACO_FEATURES.map(({ chave, label, unidade }) => (
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

          <View style={styles.botoesLinha}>
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
