import { useCallback, useState } from 'react';
import { View, Text, ScrollView, ActivityIndicator } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Avatar from '../components/Avatar';
import RiscoCard from '../components/RiscoCard';
import { useAuth } from '../context/AuthContext';
import { buscarPerfil } from '../services/api';
import { RISCO_CARDIACO_FEATURES } from '../data/riscoCardiacoFeatures';
import { colors } from '../theme/colors';
import styles from '../styles/perfilUsuarioScreenStyles';

const NIVEL_POR_CLASSIFICACAO = {
  'Alto risco': 'alto',
  'Baixo risco': 'baixo',
};

const STATUS_POR_CLASSIFICACAO = {
  'Alto risco': colors.status.critical,
  'Baixo risco': colors.status.good,
};

/** Formata uma data ISO para o padrão "dd/mm/aa hh:mm" em português. */
function formatarDataHora(iso) {
  const data = new Date(iso);
  return (
    data.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' }) +
    ' ' +
    data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  );
}

/** Tela de perfil do usuário com avatar, risco mais recente, dados da avaliação e histórico. */
export default function PerfilUsuarioScreen() {
  const { usuario } = useAuth();
  const [perfil, setPerfil] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  /** Busca o perfil do usuário logado, incluindo a avaliação mais recente. */
  const carregarPerfil = useCallback(async () => {
    if (!usuario) return;
    setCarregando(true);
    setErro(null);
    try {
      setPerfil(await buscarPerfil(usuario.id));
    } catch (e) {
      setErro(e.message);
    } finally {
      setCarregando(false);
    }
  }, [usuario]);

  useFocusEffect(
    useCallback(() => {
      carregarPerfil();
    }, [carregarPerfil])
  );

  if (carregando && !perfil) {
    return (
      <View style={styles.centro}>
        <ActivityIndicator color={colors.primary} />
      </View>
    );
  }

  if (erro) {
    return (
      <View style={styles.centro}>
        <Text style={styles.descricaoSecao}>{erro}</Text>
      </View>
    );
  }

  const avaliacao = perfil?.avaliacao_mais_recente;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.cabecalho}>
          <Avatar usuarioId={usuario?.id} nickname={usuario?.nickname} tamanho={88} />
          <Text style={styles.nickname}>{usuario?.nickname}</Text>
          <Text style={styles.email}>{usuario?.email}</Text>
        </View>

        <Text style={styles.secaoTitulo}>Risco mais recente</Text>
        {avaliacao ? (
          <RiscoCard
            condicao={`Risco de crise cardíaca (${Math.round(avaliacao.probabilidade * 100)}%)`}
            nivel={NIVEL_POR_CLASSIFICACAO[avaliacao.classificacao] ?? 'moderado'}
            descricao={avaliacao.recomendacao}
          />
        ) : (
          <Text style={styles.descricaoSecao}>
            Nenhuma avaliação ainda. Vá até a aba Previsão e avalie o risco com seus dados.
          </Text>
        )}

        {avaliacao && (
          <>
            <Text style={styles.secaoTitulo}>Dados dessa avaliação</Text>
            <View style={styles.grid}>
              {RISCO_CARDIACO_FEATURES.map(({ chave, label, unidade }) => (
                <View key={chave} style={styles.chip}>
                  <Text style={styles.chipLabel}>{label}</Text>
                  <Text style={styles.chipValor}>
                    {avaliacao.dados[chave]} {unidade}
                  </Text>
                </View>
              ))}
            </View>
          </>
        )}

        {perfil?.historico?.length > 0 && (
          <>
            <Text style={styles.secaoTitulo}>Histórico</Text>
            <View>
              {perfil.historico.map((item) => {
                const status = STATUS_POR_CLASSIFICACAO[item.classificacao] ?? colors.status.warning;
                return (
                  <View key={item.criado_em} style={styles.historicoItem}>
                    <Text style={styles.historicoData}>{formatarDataHora(item.criado_em)}</Text>
                    <View style={[styles.historicoBadge, { backgroundColor: status.bg }]}>
                      <Text style={[styles.historicoBadgeTexto, { color: status.text }]}>
                        {item.classificacao}
                      </Text>
                    </View>
                  </View>
                );
              })}
            </View>
          </>
        )}
      </View>
    </ScrollView>
  );
}
