import { View, Text, ScrollView } from 'react-native';
import { useCallback, useState } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import RiscoCard from '../components/RiscoCard';
import LoadingSpinner from '../components/LoadingSpinner';
import Disclaimer from '../components/Disclaimer';
import { buscarPerfilGenomicoAtual } from '../db/database';
import { mapearRiscos } from '../utils/perfilGenomico';
import styles from '../styles/riscosScreenStyles';

export default function HomeScreen() {
   const [carregando, setCarregando] = useState(true);
   const [riscos, setRiscos] = useState([]);

   const carregarRiscos = useCallback(async () => {
      const perfil = await buscarPerfilGenomicoAtual();
      setRiscos(mapearRiscos(perfil));
      setCarregando(false);
   }, []);

   useFocusEffect(
      useCallback(() => {
         carregarRiscos();
      }, [carregarRiscos])
   );

   if (carregando) {
      return <LoadingSpinner message="Analisando seu relatório genético..." />;
   }

   return (
      <ScrollView style={styles.container}>
         <View style={styles.content}>
            <Text style={styles.header}>Cards de Risco</Text>

            <Disclaimer texto="Estas informações são interpretações do relatório genético e não substituem um diagnóstico médico." />

            {riscos.length === 0 ? (
               <Text style={styles.vazio}>
                  Nenhum relatório enviado ainda. Vá até a aba Ancestralidade e envie seu relatório genômico.
               </Text>
            ) : (
               riscos.map(risco => (
                  <RiscoCard
                     key={risco.id}
                     condicao={risco.condicao}
                     nivel={risco.nivel}
                     descricao={risco.descricao}
                  />
               ))
            )}
         </View>
      </ScrollView>
   );
}
