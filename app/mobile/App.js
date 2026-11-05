import { useEffect, useState } from 'react';
import { Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import {
  useFonts,
  Nunito_400Regular,
  Nunito_600SemiBold,
  Nunito_700Bold,
  Nunito_800ExtraBold,
} from '@expo-google-fonts/nunito';
import { colors } from './src/theme/colors';
import { fonts } from './src/theme/typography';
import styles from './src/styles/appStyles';
import LoadingSpinner from './src/components/LoadingSpinner';
import { initDatabase } from './src/db/database';
import { AuthProvider, useAuth } from './src/context/AuthContext';
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

  if (!fontsLoaded || !dbPronto) {
    return <LoadingSpinner message="Carregando..." />;
  }

  return (
    <AuthProvider>
      <AppConteudo />
    </AuthProvider>
  );
}

/** Decide entre exibir o fluxo de autenticação ou a navegação principal em abas. */
function AppConteudo() {
  const { usuario, carregando } = useAuth();

  if (carregando) {
    return <LoadingSpinner message="Carregando..." />;
  }

  if (!usuario) {
    return (
      <NavigationContainer>
        <AuthStack />
      </NavigationContainer>
    );
  }

  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          tabBarActiveTintColor: colors.primary,
          tabBarInactiveTintColor: colors.textMuted,
          tabBarStyle: styles.tabBar,
          tabBarShowLabel: false,
          headerStyle: styles.header,
          headerTintColor: colors.white,
          headerTitleStyle: styles.headerTitle,
        }}
      >
        <Tab.Screen
          name="Dashboard"
          component={DashboardScreen}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Text style={{ fontSize: size / 2, color, fontFamily: fonts.bold }}>INÍCIO</Text>
            ),
          }}
        />

        <Tab.Screen
          name="Riscos"
          component={HomeScreen}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Text style={{ fontSize: size / 2, color, fontFamily: fonts.bold }}>RISCOS</Text>
            ),
          }}
        />

        <Tab.Screen
          name="Ancestralidade"
          component={ProfileScreen}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Text style={{ fontSize: size / 2, color, fontFamily: fonts.bold }}>DNA</Text>
            ),
          }}
        />

         <Tab.Screen
          name="Análise"
          component={AnaliseStack}
          options={{
            headerShown: false,
            tabBarIcon: ({ color, size }) => (
              <Text style={{ fontSize: size / 2, color, fontFamily: fonts.bold }}>ANÁLISE</Text>
            ),
          }}
        />

        <Tab.Screen
          name="Previsão"
          component={PrevisaoStack}
          options={{
            headerShown: false,
            tabBarIcon: ({ color, size }) => (
              <Text style={{ fontSize: size / 2, color, fontFamily: fonts.bold }}>PREVISÃO</Text>
            ),
          }}
        />

        <Tab.Screen
          name="Perfil"
          component={PerfilUsuarioScreen}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Text style={{ fontSize: size / 2, color, fontFamily: fonts.bold }}>PERFIL</Text>
            ),
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}