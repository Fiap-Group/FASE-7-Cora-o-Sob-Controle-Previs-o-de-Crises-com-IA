import { useMemo } from 'react';
import { View, Text } from 'react-native';
import ChatBox from '../components/ChatBox';
import { useTema } from '../theme/ThemeContext';
import criarEstilos from '../styles/chatScreenStyles';

/** Tela de conversa com o agente, exibindo o contexto do resumo quando houver. */
export default function ChatScreen({ route }) {
  const { colors } = useTema();
  const styles = useMemo(() => criarEstilos(colors), [colors]);
  const { sessaoId, resumoData } = route.params;

  return (
    <View style={styles.container}>
      {resumoData && (
        <View style={styles.header}>
          <Text style={styles.headerTexto}>
            Conversa sobre o resumo de{' '}
            {new Date(resumoData).toLocaleDateString('pt-BR')} às{' '}
            {new Date(resumoData).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
          </Text>
        </View>
      )}
      <ChatBox sessaoId={sessaoId} />
    </View>
  );
}
