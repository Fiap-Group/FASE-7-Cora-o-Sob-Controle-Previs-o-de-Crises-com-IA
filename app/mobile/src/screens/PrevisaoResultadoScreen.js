import { useMemo } from 'react';
import { View, Text, ScrollView } from 'react-native';
import RiscoCard from '../components/RiscoCard';
import Disclaimer from '../components/Disclaimer';
import { useTema } from '../theme/ThemeContext';
import criarEstilos from '../styles/previsaoResultadoScreenStyles';

const NIVEL_POR_CLASSIFICACAO = {
  'Alto risco': 'alto',
  'Baixo risco': 'baixo',
};

/** Tela que exibe o resultado da previsão de risco cardíaco e protocolos sugeridos. */
export default function PrevisaoResultadoScreen({ route }) {
  const { colors } = useTema();
  const styles = useMemo(() => criarEstilos(colors), [colors]);
  const { resultado } = route.params;
  const { probabilidade, classificacao, protocolos, recomendacao } = resultado;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <RiscoCard
          condicao={`Risco de crise cardíaca (${Math.round(probabilidade * 100)}%)`}
          nivel={NIVEL_POR_CLASSIFICACAO[classificacao] ?? 'moderado'}
          descricao={recomendacao}
        />

        <Text style={styles.secaoTitulo}>Protocolos sugeridos</Text>
        <View style={styles.section}>
          {protocolos.map((protocolo) => (
            <Text key={protocolo} style={styles.protocolo}>
              • {protocolo}
            </Text>
          ))}
        </View>

        <Disclaimer texto="Esta recomendação foi gerada por um sistema de IA a partir de dados sintéticos de operação. Use-a como apoio, não como decisão clínica final." />
      </View>
    </ScrollView>
  );
}
