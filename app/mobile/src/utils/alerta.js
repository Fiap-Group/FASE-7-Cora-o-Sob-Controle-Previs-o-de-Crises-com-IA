import { Alert, Platform } from 'react-native';

// No react-native-web, Alert.alert() é um stub vazio: não mostra nada e
// nunca chama os callbacks dos botões. Por isso usamos window.alert/confirm
// quando rodando na web, e o Alert nativo nas outras plataformas.

export function avisar(titulo, mensagem) {
  if (Platform.OS === 'web') {
    window.alert(mensagem ? `${titulo}\n\n${mensagem}` : titulo);
    return;
  }
  Alert.alert(titulo, mensagem);
}

export function confirmarAcao(titulo, mensagem, onConfirmar, textoConfirmar = 'Confirmar') {
  if (Platform.OS === 'web') {
    if (window.confirm(mensagem ? `${titulo}\n\n${mensagem}` : titulo)) {
      onConfirmar();
    }
    return;
  }
  Alert.alert(titulo, mensagem, [
    { text: 'Cancelar', style: 'cancel' },
    { text: textoConfirmar, style: 'destructive', onPress: onConfirmar },
  ]);
}
