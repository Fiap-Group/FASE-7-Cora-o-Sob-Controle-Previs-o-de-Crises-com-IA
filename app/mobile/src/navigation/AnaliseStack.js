import { createNativeStackNavigator } from '@react-navigation/native-stack';
import ResumosScreen from '../screens/ResumosScreen';
import ChatScreen from '../screens/ChatScreen';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

const Stack = createNativeStackNavigator();

export default function AnaliseStack() {
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
