import { createNativeStackNavigator } from '@react-navigation/native-stack';
import PrevisaoFormScreen from '../screens/PrevisaoFormScreen';
import PrevisaoResultadoScreen from '../screens/PrevisaoResultadoScreen';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

const Stack = createNativeStackNavigator();

export default function PrevisaoStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.primary },
        headerTintColor: colors.white,
        headerTitleStyle: { fontFamily: fonts.bold, fontSize: 18 },
      }}
    >
      <Stack.Screen name="PrevisaoForm" component={PrevisaoFormScreen} options={{ title: 'Previsão de Risco' }} />
      <Stack.Screen name="PrevisaoResultado" component={PrevisaoResultadoScreen} options={{ title: 'Resultado' }} />
    </Stack.Navigator>
  );
}
