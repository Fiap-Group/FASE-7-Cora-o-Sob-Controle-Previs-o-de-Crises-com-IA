import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { useCallback, useState } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import RiscoCard from '../components/RiscoCard';
import AncestralidadeBarra from '../components/AncestralidadeBarra';
import Disclaimer from '../components/Disclaimer';
import { buscarPerfilGenomicoAtual } from '../db/database';
import { mapearRiscos, riscoDeMaiorSeveridade, topAncestralidade } from '../utils/perfilGenomico';
import styles from '../styles/dashboardScreenStyles';

export default function DashboardScreen({ navigation }) {
  const [riscoDestaque, setRiscoDestaque] = useState(null);
  const [ancestralidadeDestaque, setAncestralidadeDestaque] = useState([]);

  const carregarDestaques = useCallback(async () => {
    const perfil = await buscarPerfilGenomicoAtual();
    setRiscoDestaque(riscoDeMaiorSeveridade(mapearRiscos(perfil)));
    setAncestralidadeDestaque(topAncestralidade(perfil, 2));
  }, []);

  useFocusEffect(
    useCallback(() => {
      carregarDestaques();
    }, [carregarDestaques])
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.saudacao}>Olá!</Text>
        <Text style={styles.subtitulo}>Aqui está um resumo do seu perfil genético.</Text>

        <Disclaimer texto="As informações a seguir são interpretações do seu relatório genético e não substituem uma avaliação médica." />

        <View style={styles.secao}>
          <View style={styles.secaoHeader}>
            <Text style={styles.secaoTitulo}>Principal Atenção</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Riscos')}>
              <Text style={styles.verTudo}>Ver todos →</Text>
            </TouchableOpacity>
          </View>
          {riscoDestaque ? (
            <RiscoCard {...riscoDestaque} />
          ) : (
            <Text style={styles.descricaoSecao}>
              Nenhum relatório enviado ainda. Vá até a aba Ancestralidade e envie seu relatório genômico.
            </Text>
          )}
        </View>

        <View style={styles.secao}>
          <View style={styles.secaoHeader}>
            <Text style={styles.secaoTitulo}>Ancestralidade</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Ancestralidade')}>
              <Text style={styles.verTudo}>Ver tudo →</Text>
            </TouchableOpacity>
          </View>
          {ancestralidadeDestaque.length > 0 ? (
            ancestralidadeDestaque.map((item) => <AncestralidadeBarra key={item.regiao} {...item} />)
          ) : (
            <Text style={styles.descricaoSecao}>
              Nenhum relatório enviado ainda. Vá até a aba Ancestralidade e envie seu relatório genômico.
            </Text>
          )}
        </View>

        <View style={styles.secao}>
          <View style={styles.secaoHeader}>
            <Text style={styles.secaoTitulo}>Resumos e Agente</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Análise')}>
              <Text style={styles.verTudo}>Ver resumos →</Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.descricaoSecao}>
            Veja os resumos gerados a cada nova leva de dados e converse com o assistente de IA sobre eles.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}
