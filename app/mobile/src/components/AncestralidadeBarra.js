import { useMemo } from 'react';
import { View, Text } from 'react-native';
import { useTema } from '../theme/ThemeContext';
import criarEstilos from '../styles/ancestralidadeBarraStyles';

/** Exibe uma barra de progresso representando o percentual de ancestralidade de uma região. */
export default function AncestralidadeBarra({ regiao, percentual }) {
  const { colors } = useTema();
  const styles = useMemo(() => criarEstilos(colors), [colors]);

  return (
    <View style={styles.container}>
      <View style={styles.linhaTexto}>
        <Text style={styles.regiao}>{regiao}</Text>
        <Text style={styles.percentual}>{percentual}%</Text>
      </View>
      <View style={styles.trilha}>
        <View style={[styles.barra, { width: `${percentual}%` }]} />
      </View>
    </View>
  );
}
