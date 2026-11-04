import { useCallback, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import ResumoCard from '../components/ResumoCard';
import { buscarResumos, deletarResumo } from '../db/database';
import { gerarNovoResumo } from '../services/resumoService';
import { avisar, confirmarAcao } from '../utils/alerta';
import { colors } from '../theme/colors';
import styles from '../styles/resumosScreenStyles';

export default function ResumosScreen({ navigation }) {
  const [resumos, setResumos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [gerando, setGerando] = useState(false);

  const carregarResumos = useCallback(async () => {
    const lista = await buscarResumos();
    setResumos(lista);
    setCarregando(false);
  }, []);

  useFocusEffect(
    useCallback(() => {
      carregarResumos();
    }, [carregarResumos])
  );

  const handleGerarResumo = async () => {
    setGerando(true);
    // Simula a chegada de uma nova leva de dados do relatório (ex: nova semana).
    // Em produção, este gatilho seria automático a cada nova inserção de dados.
    try {
      await gerarNovoResumo();
      await carregarResumos();
    } catch (erro) {
      const semRelatorio = erro.message?.startsWith('Nenhum relatório enviado');
      avisar(
        'Não foi possível gerar o resumo',
        semRelatorio
          ? erro.message
          : `Verifique se o backend está rodando e se a chave de API foi configurada.\n\n${erro.message}`
      );
    } finally {
      setGerando(false);
    }
  };

  const abrirResumo = (resumo) => {
    navigation.navigate('Chat', { sessaoId: resumo.sessao_id, resumoData: resumo.data_criacao });
  };

  const handleRemover = (resumo) => {
    confirmarAcao(
      'Remover resumo',
      'Isso vai apagar este resumo e toda a conversa associada a ele. Deseja continuar?',
      async () => {
        await deletarResumo(resumo.id, resumo.sessao_id);
        await carregarResumos();
      },
      'Remover'
    );
  };

  if (carregando) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color={colors.primary} size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.titulo}>Resumos</Text>
        <TouchableOpacity style={styles.botaoGerar} onPress={handleGerarResumo} disabled={gerando}>
          <Text style={styles.botaoGerarTexto}>{gerando ? 'Gerando...' : '+ Novo Resumo'}</Text>
        </TouchableOpacity>
      </View>

      {resumos.length === 0 ? (
        <Text style={styles.vazio}>Nenhum resumo ainda. Toque em "+ Novo Resumo" para gerar o primeiro.</Text>
      ) : (
        <FlatList
          data={resumos}
          keyExtractor={(item) => String(item.id)}
          contentContainerStyle={styles.lista}
          renderItem={({ item }) => (
            <ResumoCard
              dataCriacao={item.data_criacao}
              onPress={() => abrirResumo(item)}
              onRemover={() => handleRemover(item)}
            />
          )}
        />
      )}
    </View>
  );
}
