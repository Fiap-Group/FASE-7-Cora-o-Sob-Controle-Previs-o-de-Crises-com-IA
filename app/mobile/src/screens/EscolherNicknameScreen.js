import { useMemo, useState } from 'react';
import { View, Text, ScrollView, TextInput, TouchableOpacity } from 'react-native';
import { definirNickname } from '../services/api';
import { definirSessao } from '../db/database';
import { useAuth } from '../context/AuthContext';
import { avisar } from '../utils/alerta';
import { useTema } from '../theme/ThemeContext';
import criarEstilos from '../styles/loginScreenStyles';

/** Tela de escolha do nickname ao final do cadastro. */
export default function EscolherNicknameScreen({ route }) {
  const { usuarioId } = route.params;
  const { recarregarSessao } = useAuth();
  const { colors } = useTema();
  const styles = useMemo(() => criarEstilos(colors), [colors]);
  const [nickname, setNickname] = useState('');
  const [salvando, setSalvando] = useState(false);

  /** Salva o nickname escolhido e inicia a sessão do usuário. */
  const handleConfirmar = async () => {
    if (!nickname.trim()) {
      avisar('Escolha um nickname');
      return;
    }

    setSalvando(true);
    try {
      const usuario = await definirNickname(usuarioId, nickname.trim());
      await definirSessao(usuario);
      await recarregarSessao();
    } catch (erro) {
      avisar('Não foi possível salvar o nickname', erro.message);
    } finally {
      setSalvando(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.titulo}>Quase lá!</Text>
      <Text style={styles.introducao}>Escolha um nickname para a sua conta.</Text>

      <View style={styles.formulario}>
        <View style={styles.campo}>
          <Text style={styles.label}>Nickname</Text>
          <TextInput
            style={styles.inputTexto}
            value={nickname}
            onChangeText={setNickname}
            placeholder="Como quer ser chamado?"
            editable={!salvando}
            autoFocus
          />
        </View>

        <TouchableOpacity
          style={[styles.botaoPrimario, salvando && styles.botaoDesabilitado]}
          onPress={handleConfirmar}
          disabled={salvando}
        >
          <Text style={styles.botaoPrimarioTexto}>{salvando ? 'Salvando...' : 'Concluir cadastro'}</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}
