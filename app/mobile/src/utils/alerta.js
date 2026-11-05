import { Alert, Platform } from 'react-native';

/** Exibe um alerta simples, usando window.alert na web e Alert nativo nas demais plataformas. */
export function avisar(titulo, mensagem) {
  if (Platform.OS === 'web') {
    window.alert(mensagem ? `${titulo}\n\n${mensagem}` : titulo);
    return;
  }
  Alert.alert(titulo, mensagem);
}

/** Exibe uma confirmação com opções de cancelar ou confirmar, executando o callback informado. */
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
