import { View, ActivityIndicator, Text } from 'react-native';
import { colors } from '../theme/colors';
import styles from '../styles/loadingSpinnerStyles';

export default function LoadingSpinner({ message = 'Carregando...', size = 'large' }) {
   return (
      <View style={styles.container}>
         <ActivityIndicator size={size} color={colors.primary} />
         {message && <Text style={styles.message}>{message}</Text>}
      </View>
   );
}
