import { createNativeStackNavigator } from '@react-navigation/native-stack';
import LoginScreen from '../screens/LoginScreen';
import CadastroScreen from '../screens/CadastroScreen';
import EscolherNicknameScreen from '../screens/EscolherNicknameScreen';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

const Stack = createNativeStackNavigator();

/** Define a navegação em pilha das telas de login, cadastro e escolha de nickname. */
export default function AuthStack() {
  return (
    <Stack.Navigator
      initialRouteName="Login"
      screenOptions={{
        headerStyle: { backgroundColor: colors.primary },
        headerTintColor: colors.white,
        headerTitleStyle: { fontFamily: fonts.bold, fontSize: 18 },
      }}
    >
      <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
      <Stack.Screen name="Cadastro" component={CadastroScreen} options={{ title: 'Criar conta' }} />
      <Stack.Screen
        name="EscolherNickname"
        component={EscolherNicknameScreen}
        options={{ title: 'Nickname', headerBackVisible: false }}
      />
    </Stack.Navigator>
  );
}
