import { createNativeStackNavigator } from '@react-navigation/native-stack';
import ResumosScreen from '../screens/ResumosScreen';
import ChatScreen from '../screens/ChatScreen';
import { useTema } from '../theme/ThemeContext';
import { fonts } from '../theme/typography';

const Stack = createNativeStackNavigator();

/** Define a navegação em pilha das telas de resumos e conversa com o agente. */
export default function AnaliseStack() {
  const { colors } = useTema();

  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.primary },
        headerTintColor: colors.white,
        headerTitleStyle: { fontFamily: fonts.bold, fontSize: 18 },
      }}
    >
      <Stack.Screen name="Resumos" component={ResumosScreen} options={{ title: 'Resumos' }} />
      <Stack.Screen name="Chat" component={ChatScreen} options={{ title: 'Conversa' }} />
    </Stack.Navigator>
  );
}
