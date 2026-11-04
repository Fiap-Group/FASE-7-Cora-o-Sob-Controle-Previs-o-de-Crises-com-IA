import { View, Text } from 'react-native';
import styles from '../styles/disclaimerStyles';

export default function Disclaimer({ texto }) {
  return (
    <View style={styles.container}>
      <Text style={styles.texto}>{texto}</Text>
    </View>
  );
}
