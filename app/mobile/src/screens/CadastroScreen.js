import { useState } from 'react';
import { View, Text, ScrollView, TextInput, TouchableOpacity } from 'react-native';
import { cadastrar } from '../services/api';
import { avisar } from '../utils/alerta';
import styles from '../styles/loginScreenStyles';

const REGEX_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function CadastroScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [cadastrando, setCadastrando] = useState(false);

  const emailValido = REGEX_EMAIL.test(email.trim());
  const podeEnviar = emailValido && senha.trim().length > 0 && !cadastrando;

  const handleCadastrar = async () => {
    if (!podeEnviar) return;

    setCadastrando(true);
    try {
      const usuario = await cadastrar(email.trim(), senha);
      navigation.navigate('EscolherNickname', { usuarioId: usuario.id });
    } catch (erro) {
      avisar('Não foi possível criar a conta', erro.message);
    } finally {
      setCadastrando(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.titulo}>Criar conta</Text>
      <Text style={styles.introducao}>Cadastre-se para acompanhar os indicadores de risco cardíaco.</Text>

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
            editable={!cadastrando}
          />
          {email.trim().length > 0 && !emailValido && <Text style={styles.erroTexto}>E-mail inválido</Text>}
        </View>

        <View style={styles.campo}>
          <Text style={styles.label}>Senha</Text>
          <TextInput
            style={styles.inputTexto}
            value={senha}
            onChangeText={setSenha}
            placeholder="••••••••"
            secureTextEntry
            editable={!cadastrando}
          />
        </View>

        <TouchableOpacity
          style={[styles.botaoPrimario, !podeEnviar && styles.botaoDesabilitado]}
          onPress={handleCadastrar}
          disabled={!podeEnviar}
        >
          <Text style={styles.botaoPrimarioTexto}>{cadastrando ? 'Criando...' : 'Criar conta'}</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.linkAlternar} onPress={() => navigation.navigate('Login')}>
        <Text style={styles.linkAlternarTexto}>Já tem conta? Entrar</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}
