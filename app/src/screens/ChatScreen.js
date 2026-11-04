import { View, Text } from 'react-native';
import ChatBox from '../components/ChatBox';
import styles from '../styles/chatScreenStyles';

export default function ChatScreen({ route }) {
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
