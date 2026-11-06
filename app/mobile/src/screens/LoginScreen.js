import { useMemo, useState } from 'react';
import { View, Text, ScrollView, TextInput, TouchableOpacity } from 'react-native';
import { login } from '../services/api';
import { definirSessao } from '../db/database';
import { useAuth } from '../context/AuthContext';
import { avisar } from '../utils/alerta';
import { useTema } from '../theme/ThemeContext';
import criarEstilos from '../styles/loginScreenStyles';

/** Tela de login de usuário por e-mail e senha. */
export default function LoginScreen({ navigation }) {
  const { recarregarSessao } = useAuth();
  const { colors } = useTema();
  const styles = useMemo(() => criarEstilos(colors), [colors]);
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [entrando, setEntrando] = useState(false);

  /** Autentica o usuário e inicia a sessão. */
  const handleEntrar = async () => {
    if (!email.trim() || !senha.trim()) {
      avisar('Preencha e-mail e senha');
      return;
    }

    setEntrando(true);
    try {
      const usuario = await login(email.trim(), senha);
      await definirSessao(usuario);
      await recarregarSessao();
    } catch (erro) {
      avisar('Não foi possível entrar', erro.message);
    } finally {
      setEntrando(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.titulo}>CardioIA</Text>
      <Text style={styles.introducao}>Entre com sua conta para acompanhar os indicadores de risco.</Text>

      <View style={styles.formulario}>
        <View style={styles.campo}>
          <Text style={styles.label}>E-mail</Text>
          <TextInput
            style={styles.inputTexto}
            value={email}
            onChangeText={setEmail}
            placeholder="voce@exemplo.com"
            keyboardType="email-address"
            autoCapitalize="none"
            editable={!entrando}
          />
        </View>

        <View style={styles.campo}>
          <Text style={styles.label}>Senha</Text>
          <TextInput
            style={styles.inputTexto}
            value={senha}
            onChangeText={setSenha}
            placeholder="••••••••"
            secureTextEntry
            editable={!entrando}
          />
        </View>

        <TouchableOpacity
          style={[styles.botaoPrimario, entrando && styles.botaoDesabilitado]}
          onPress={handleEntrar}
          disabled={entrando}
        >
          <Text style={styles.botaoPrimarioTexto}>{entrando ? 'Entrando...' : 'Entrar'}</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.linkAlternar} onPress={() => navigation.navigate('Cadastro')}>
        <Text style={styles.linkAlternarTexto}>Não tem conta? Cadastre-se</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}
