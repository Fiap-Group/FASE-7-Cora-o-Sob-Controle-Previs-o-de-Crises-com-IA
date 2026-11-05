import { Text, TouchableOpacity, View } from 'react-native';
import styles from '../styles/resumoCardStyles';

function formatarDataHora(dataIso) {
  const data = new Date(dataIso);
  const dataFormatada = data.toLocaleDateString('pt-BR');
  const horaFormatada = data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  return `${dataFormatada} às ${horaFormatada}`;
}

// Lixeira e área de abrir o chat são TouchableOpacity IRMÃS (não uma dentro
// da outra) — TouchableOpacity aninhada em TouchableOpacity é instável no
// react-native-web (o sistema de "responder" às vezes não dispara nenhuma
// das duas).
export default function ResumoCard({ dataCriacao, onPress, onRemover }) {
  return (
    <View style={styles.card}>
      <TouchableOpacity style={styles.conteudoClicavel} onPress={onPress}>
        <Text style={styles.titulo}>RESUMO</Text>
        <Text style={styles.data}>{formatarDataHora(dataCriacao)}</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.botaoRemover}
        onPress={onRemover}
        hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
      >
        <Text style={styles.iconeRemover}>🗑️</Text>
      </TouchableOpacity>
    </View>
  );
}
