import { useMemo } from 'react';
import { View, ActivityIndicator, Text } from 'react-native';
import { useTema } from '../theme/ThemeContext';
import criarEstilos from '../styles/loadingSpinnerStyles';

/** Exibe um indicador de carregamento com mensagem opcional. */
export default function LoadingSpinner({ message = 'Carregando...', size = 'large' }) {
   const { colors } = useTema();
   const styles = useMemo(() => criarEstilos(colors), [colors]);

   return (
      <View style={styles.container}>
         <ActivityIndicator size={size} color={colors.primary} />
         {message && <Text style={styles.message}>{message}</Text>}
      </View>
   );
}
