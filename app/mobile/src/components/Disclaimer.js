import { useMemo } from 'react';
import { View, Text } from 'react-native';
import { useTema } from '../theme/ThemeContext';
import criarEstilos from '../styles/disclaimerStyles';

/** Exibe um texto de aviso/disclaimer em destaque. */
export default function Disclaimer({ texto }) {
  const { colors } = useTema();
  const styles = useMemo(() => criarEstilos(colors), [colors]);

  return (
    <View style={styles.container}>
      <Text style={styles.texto}>{texto}</Text>
    </View>
  );
}
