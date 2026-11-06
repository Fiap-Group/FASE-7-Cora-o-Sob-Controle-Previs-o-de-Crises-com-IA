import { useEffect, useMemo, useState } from 'react';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { NavigationContainer, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import {
  useFonts,
  Nunito_400Regular,
  Nunito_600SemiBold,
  Nunito_700Bold,
  Nunito_800ExtraBold,
} from '@expo-google-fonts/nunito';
import criarEstilos from './src/styles/appStyles';
import LoadingSpinner from './src/components/LoadingSpinner';
import { initDatabase } from './src/db/database';
import { AuthProvider, useAuth } from './src/context/AuthContext';
import { ThemeProvider, useTema } from './src/theme/ThemeContext';
import AuthStack from './src/navigation/AuthStack';

import DashboardScreen from './src/screens/DashboardScreen';
import HomeScreen from './src/screens/HomeScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import PerfilUsuarioScreen from './src/screens/PerfilUsuarioScreen';
import AnaliseStack from './src/navigation/AnaliseStack';
import PrevisaoStack from './src/navigation/PrevisaoStack';
const Tab = createBottomTabNavigator();

/** Componente raiz: carrega fontes e banco local, e provê o contexto de autenticação. */
export default function App() {
  const [fontsLoaded] = useFonts({
    Nunito_400Regular,
    Nunito_600SemiBold,
    Nunito_700Bold,
    Nunito_800ExtraBold,
  });
  const [dbPronto, setDbPronto] = useState(false);

  useEffect(() => {
    initDatabase().then(() => setDbPronto(true));
  }, []);

  return (
    <ThemeProvider>
      {!fontsLoaded || !dbPronto ? (
        <LoadingSpinner message="Carregando..." />
      ) : (
        <AuthProvider>
          <AppConteudo />
        </AuthProvider>
      )}
    </ThemeProvider>
  );
}

/** Decide entre exibir o fluxo de autenticação ou a navegação principal em abas. */
function AppConteudo() {
  const { usuario, carregando } = useAuth();
  const { colors, esquema } = useTema();
  const styles = useMemo(() => criarEstilos(colors), [colors]);

  const baseNavegacao = esquema === 'dark' ? DarkTheme : DefaultTheme;
  const temaNavegacao = {
    ...baseNavegacao,
    colors: {
      ...baseNavegacao.colors,
      background: colors.background,
      card: colors.surface,
      text: colors.textPrimary,
      border: colors.border,
      primary: colors.primary,
    },
  };

  if (carregando) {
    return <LoadingSpinner message="Carregando..." />;
  }

  if (!usuario) {
    return (
      <NavigationContainer theme={temaNavegacao}>
        <AuthStack />
      </NavigationContainer>
    );
  }

  return (
    <NavigationContainer theme={temaNavegacao}>
      <Tab.Navigator
        screenOptions={{
          tabBarActiveTintColor: colors.primary,
          tabBarInactiveTintColor: colors.textMuted,
          tabBarStyle: styles.tabBar,
          tabBarLabelStyle: styles.tabBarLabel,
          headerStyle: styles.header,
          headerTintColor: colors.white,
          headerTitleStyle: styles.headerTitle,
        }}
      >
        <Tab.Screen
          name="Dashboard"
          component={DashboardScreen}
          options={{
            title: 'Início',
            tabBarIcon: ({ color, size, focused }) => (
              <Ionicons name={focused ? 'home' : 'home-outline'} size={size} color={color} />
            ),
          }}
        />

        <Tab.Screen
          name="Riscos"
          component={HomeScreen}
          options={{
            tabBarIcon: ({ color, size, focused }) => (
              <Ionicons name={focused ? 'pulse' : 'pulse-outline'} size={size} color={color} />
            ),
          }}
        />

        <Tab.Screen
          name="Ancestralidade"
          component={ProfileScreen}
          options={{
            title: 'DNA',
            tabBarIcon: ({ color, size }) => <MaterialCommunityIcons name="dna" size={size} color={color} />,
          }}
        />

         <Tab.Screen
          name="Análise"
          component={AnaliseStack}
          options={{
            headerShown: false,
            tabBarIcon: ({ color, size, focused }) => (
              <Ionicons name={focused ? 'chatbubbles' : 'chatbubbles-outline'} size={size} color={color} />
            ),
          }}
        />

        <Tab.Screen
          name="Previsão"
          component={PrevisaoStack}
          options={{
            headerShown: false,
            tabBarIcon: ({ color, size, focused }) => (
              <Ionicons name={focused ? 'analytics' : 'analytics-outline'} size={size} color={color} />
            ),
          }}
        />

        <Tab.Screen
          name="Perfil"
          component={PerfilUsuarioScreen}
          options={{
            tabBarIcon: ({ color, size, focused }) => (
              <Ionicons name={focused ? 'person' : 'person-outline'} size={size} color={color} />
            ),
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}