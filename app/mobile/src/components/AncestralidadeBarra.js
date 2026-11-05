import { View, Text } from 'react-native';
import styles from '../styles/ancestralidadeBarraStyles';

/** Exibe uma barra de progresso representando o percentual de ancestralidade de uma região. */
export default function AncestralidadeBarra({ regiao, percentual }) {
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
