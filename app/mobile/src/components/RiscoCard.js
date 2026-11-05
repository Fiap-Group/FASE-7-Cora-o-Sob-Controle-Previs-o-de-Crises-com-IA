import { View, Text } from 'react-native';
import { colors } from '../theme/colors';
import styles from '../styles/riscoCardStyles';

const NIVEL_STATUS = {
  baixo: colors.status.good,
  moderado: colors.status.warning,
  alto: colors.status.serious,
  'muito alto': colors.status.critical,
};

const NIVEL_LABEL = {
  baixo: 'Risco Baixo',
  moderado: 'Risco Moderado',
  alto: 'Risco Alto',
  'muito alto': 'Risco Muito Alto',
};

export default function RiscoCard({ condicao, nivel, descricao }) {
  const status = NIVEL_STATUS[nivel] ?? colors.status.good;

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.condicao}>{condicao}</Text>
        <View style={[styles.badge, { backgroundColor: status.bg }]}>
          <Text style={[styles.badgeText, { color: status.text }]}>{NIVEL_LABEL[nivel] ?? nivel}</Text>
        </View>
      </View>
      <Text style={styles.descricao}>{descricao}</Text>
    </View>
  );
}
