import { View, Text } from 'react-native';
import styles from '../styles/avatarStyles';

const PALETA_CORES = ['#2a78d6', '#d6762a', '#2ad6a0', '#a02ad6', '#d62a5e', '#5e9e2a'];

/** Exibe um círculo colorido com a inicial do nickname do usuário, como avatar. */
export default function Avatar({ usuarioId, nickname, tamanho = 72 }) {
  const cor = PALETA_CORES[(usuarioId ?? 0) % PALETA_CORES.length];
  const inicial = (nickname || '?').trim().charAt(0).toUpperCase();

  return (
    <View
      style={[
        styles.circulo,
        { width: tamanho, height: tamanho, borderRadius: tamanho / 2, backgroundColor: cor },
      ]}
    >
      <Text style={[styles.inicial, { fontSize: tamanho / 2 }]}>{inicial}</Text>
    </View>
  );
}
