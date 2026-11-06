import { useMemo } from 'react';
import { Text, TouchableOpacity, View } from 'react-native';
import { useTema } from '../theme/ThemeContext';
import criarEstilos from '../styles/resumoCardStyles';

/** Formata uma data ISO para o padrão "dd/mm/aaaa às hh:mm" em português. */
function formatarDataHora(dataIso) {
  const data = new Date(dataIso);
  const dataFormatada = data.toLocaleDateString('pt-BR');
  const horaFormatada = data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  return `${dataFormatada} às ${horaFormatada}`;
}

/** Exibe um cartão de resumo com data de criação, permitindo abrir ou remover. */
export default function ResumoCard({ dataCriacao, onPress, onRemover }) {
  const { colors } = useTema();
  const styles = useMemo(() => criarEstilos(colors), [colors]);

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
