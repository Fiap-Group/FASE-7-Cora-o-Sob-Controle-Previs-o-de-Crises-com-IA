import { View, Text, ScrollView, TextInput, TouchableOpacity } from 'react-native';
import { useCallback, useRef, useState } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import AncestralidadeBarra from '../components/AncestralidadeBarra';
import LoadingSpinner from '../components/LoadingSpinner';
import Dropdown from '../components/Dropdown';
import {
  apagarTodosOsDados,
  buscarPerfilGenomicoAtual,
  registrarConsentimento,
  salvarPerfilGenomico,
  temConsentimento,
} from '../db/database';
import { apagarIndiceNoBackend, indexarRelatorio } from '../services/api';
import { gerarNovoResumo } from '../services/resumoService';
import { mapearAncestralidade, mapearNivelRisco } from '../utils/perfilGenomico';
import { avisar, confirmarAcao } from '../utils/alerta';
import relatorioGenomicoExemplo from '../data/relatorioGenomico';
import styles from '../styles/ancestralidadeScreenStyles';

const OPCOES_SEXO = [
  { label: 'Prefiro não informar', value: 'nao_informado' },
  { label: 'Feminino', value: 'feminino' },
  { label: 'Masculino', value: 'masculino' },
];

const OPCOES_NIVEL_RISCO = [
  { label: 'Baixo', value: 'baixo' },
  { label: 'Moderado', value: 'moderado' },
  { label: 'Alto', value: 'alto' },
  { label: 'Muito alto', value: 'muito alto' },
];

export default function ProfileScreen({ navigation }) {
  const [carregando, setCarregando] = useState(true);
  const [perfil, setPerfil] = useState(null);
  const [ancestralidade, setAncestralidade] = useState([]);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [enviando, setEnviando] = useState(false);

  const [pacienteNome, setPacienteNome] = useState('');
  const [pacienteDataNascimento, setPacienteDataNascimento] = useState('');
  const [pacienteSexo, setPacienteSexo] = useState('nao_informado');
  const [ancestralidadeLinhas, setAncestralidadeLinhas] = useState([
    { id: 'anc-0', origem: '', percentual: '' },
  ]);
  const [riscosLinhas, setRiscosLinhas] = useState([
    { id: 'risco-0', nome: '', nivel: 'moderado', descricao: '' },
  ]);

  const primeiraCarga = useRef(true);
  const contadorId = useRef(0);
  const novoId = (prefixo) => {
    contadorId.current += 1;
    return `${prefixo}-${contadorId.current}`;
  };

  const preencherFormularioComPerfil = (dados) => {
    if (!dados) return;
    setPacienteNome(dados.paciente?.nome || '');
    setPacienteDataNascimento(dados.paciente?.data_nascimento || '');
    setPacienteSexo(dados.paciente?.sexo || 'nao_informado');
    setAncestralidadeLinhas(
      (dados.ancestralidade?.composicao || []).map((item) => ({
        id: novoId('anc'),
        origem: item.origem || '',
        percentual: item.percentual != null ? String(item.percentual) : '',
      }))
    );
    setRiscosLinhas(
      (dados.riscos_doencas || []).map((item) => ({
        id: novoId('risco'),
        nome: item.nome || '',
        nivel: mapearNivelRisco(item.nivel_risco).nivel,
        descricao: item.descricao || '',
      }))
    );
  };

  const carregarPerfil = useCallback(async () => {
    const perfilSalvo = await buscarPerfilGenomicoAtual();
    setPerfil(perfilSalvo);
    setAncestralidade(mapearAncestralidade(perfilSalvo));
    if (primeiraCarga.current) {
      setMostrarFormulario(!perfilSalvo);
      primeiraCarga.current = false;
    }
    setCarregando(false);
  }, []);

  useFocusEffect(
    useCallback(() => {
      carregarPerfil();
    }, [carregarPerfil])
  );

  const handleUsarExemplo = () => {
    preencherFormularioComPerfil(relatorioGenomicoExemplo);
  };

  const handleAbrirNovoRelatorio = () => {
    preencherFormularioComPerfil(perfil);
    setMostrarFormulario(true);
  };

  const atualizarAncestralidadeLinha = (id, campo, valor) => {
    setAncestralidadeLinhas((atual) =>
      atual.map((linha) => (linha.id === id ? { ...linha, [campo]: valor } : linha))
    );
  };

  const adicionarAncestralidadeLinha = () => {
    setAncestralidadeLinhas((atual) => [...atual, { id: novoId('anc'), origem: '', percentual: '' }]);
  };

  const removerAncestralidadeLinha = (id) => {
    setAncestralidadeLinhas((atual) => atual.filter((linha) => linha.id !== id));
  };

  const atualizarRiscoLinha = (id, campo, valor) => {
    setRiscosLinhas((atual) => atual.map((linha) => (linha.id === id ? { ...linha, [campo]: valor } : linha)));
  };

  const adicionarRiscoLinha = () => {
    setRiscosLinhas((atual) => [...atual, { id: novoId('risco'), nome: '', nivel: 'moderado', descricao: '' }]);
  };

  const removerRiscoLinha = (id) => {
    setRiscosLinhas((atual) => atual.filter((linha) => linha.id !== id));
  };

  const montarRelatorio = () => {
    const ancestralidadeValida = ancestralidadeLinhas
      .map((linha) => ({
        origem: linha.origem.trim(),
        percentual: Number(String(linha.percentual).replace(',', '.')),
      }))
      .filter((linha) => linha.origem && !Number.isNaN(linha.percentual));

    const riscosValidos = riscosLinhas
      .map((linha) => ({
        nome: linha.nome.trim(),
        nivel_risco: linha.nivel,
        descricao: linha.descricao.trim(),
      }))
      .filter((linha) => linha.nome);

    return {
      paciente: {
        id: `PAC-${Date.now()}`,
        nome: pacienteNome.trim(),
        data_nascimento: pacienteDataNascimento.trim(),
        sexo: pacienteSexo,
        data_exame: new Date().toLocaleDateString('pt-BR'),
        laboratorio: 'Dasa/Genera',
      },
      ancestralidade: { composicao: ancestralidadeValida },
      riscos_doencas: riscosValidos,
      bem_estar: {},
      recomendacoes: {},
    };
  };

  const handleEnviar = async () => {
    if (!pacienteNome.trim()) {
      avisar('Nome obrigatório', 'Informe seu nome antes de enviar.');
      return;
    }

    const perfilMontado = montarRelatorio();

    if (perfilMontado.ancestralidade.composicao.length === 0) {
      avisar('Ancestralidade obrigatória', 'Adicione ao menos uma região de ancestralidade com percentual válido.');
      return;
    }

    // LGPD: o primeiro envio exige autorização explícita (dado de saúde, Art. 11).
    // Sem ela, nada é enviado ao backend nem salvo no dispositivo.
    if (await temConsentimento()) {
      return enviarRelatorio(perfilMontado);
    }
    confirmarAcao(
      'Autorização para usar seus dados',
      'Seu relatório tem informações genéticas (dados de saúde). Elas serão usadas só para explicar o seu ' +
        'relatório. Parte do texto é enviada ao serviço de IA do Google, sem seu nome e sem sua data de ' +
        'nascimento. Você pode apagar tudo depois, quando quiser. Você autoriza?',
      async () => {
        await registrarConsentimento();
        await enviarRelatorio(perfilMontado);
      },
      'Autorizar'
    );
  };

  const enviarRelatorio = async (perfilMontado) => {
    setEnviando(true);
    try {
      await indexarRelatorio(perfilMontado);
      await salvarPerfilGenomico(perfilMontado);

      setPerfil(perfilMontado);
      setAncestralidade(mapearAncestralidade(perfilMontado));
      setMostrarFormulario(false);

      const resumo = await gerarNovoResumo();
      navigation.navigate('Análise', {
        screen: 'Chat',
        params: { sessaoId: resumo.sessao_id, resumoData: resumo.data_criacao },
      });
    } catch (erro) {
      const semRelatorio = erro.message?.startsWith('Nenhum relatório enviado');
      avisar(
        'Não foi possível concluir o envio',
        semRelatorio
          ? erro.message
          : 'Seus dados podem já ter sido salvos, mas a geração do resumo falhou. Verifique se o backend ' +
            'está rodando e se a chave de API foi configurada. Você pode tentar ' +
            `gerar o resumo depois em Análise → "+ Novo Resumo".\n\n${erro.message}`
      );
    } finally {
      setEnviando(false);
    }
  };

  // LGPD (direito de eliminação): apaga no dispositivo e no índice do backend.
  const handleApagarDados = () => {
    confirmarAcao(
      'Apagar meus dados',
      'Isso remove do seu dispositivo o relatório, o histórico de conversas e os resumos, e apaga o ' +
        'índice do backend. Não dá para desfazer.',
      async () => {
        await apagarIndiceNoBackend();
        await apagarTodosOsDados();
        setPerfil(null);
        setAncestralidade([]);
        setMostrarFormulario(true);
        avisar('Dados apagados', 'Todos os seus dados foram removidos deste dispositivo.');
      },
      'Apagar'
    );
  };

  if (carregando) {
    return <LoadingSpinner message="Carregando seu perfil genético..." />;
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.sectionTitle}>Resumo da Ancestralidade</Text>
        <Text style={styles.introducao}>
          Estimativa da composição da sua ancestralidade, com base nas variantes analisadas no seu relatório de DNA.
        </Text>

        {perfil ? (
          <>
            <View style={styles.section}>
              {ancestralidade.map((item) => (
                <AncestralidadeBarra key={item.regiao} regiao={item.regiao} percentual={item.percentual} />
              ))}
            </View>

            {!mostrarFormulario && (
              <TouchableOpacity style={styles.linkApagarDados} onPress={handleApagarDados}>
                <Text style={styles.linkApagarDadosTexto}>Apagar meus dados</Text>
              </TouchableOpacity>
            )}

            {!mostrarFormulario && (
              <TouchableOpacity style={styles.linkNovoRelatorio} onPress={handleAbrirNovoRelatorio}>
                <Text style={styles.linkNovoRelatorioTexto}>Enviar novo relatório →</Text>
              </TouchableOpacity>
            )}
          </>
        ) : (
          <Text style={styles.vazioTexto}>
            Nenhum relatório enviado ainda. Preencha os campos abaixo para começar.
          </Text>
        )}

        {mostrarFormulario && (
          <View style={styles.formulario}>
            <Text style={styles.tituloFormulario}>Enviar relatório genômico</Text>

            {perfil && (
              <TouchableOpacity
                style={styles.linkAdicionar}
                onPress={() => setMostrarFormulario(false)}
                disabled={enviando}
              >
                <Text style={styles.linkAdicionarTexto}>← Cancelar e voltar ao resumo</Text>
              </TouchableOpacity>
            )}

            <View style={styles.campo}>
              <Text style={styles.label}>Nome</Text>
              <TextInput
                style={styles.inputTexto}
                value={pacienteNome}
                onChangeText={setPacienteNome}
                placeholder="Seu nome"
                editable={!enviando}
              />
            </View>

            <View style={styles.linhaDupla}>
              <View style={styles.campoMetade}>
                <Text style={styles.label}>Data de nascimento</Text>
                <TextInput
                  style={styles.inputTexto}
                  value={pacienteDataNascimento}
                  onChangeText={setPacienteDataNascimento}
                  placeholder="DD/MM/AAAA"
                  editable={!enviando}
                />
              </View>
              <View style={styles.campoMetade}>
                <Text style={styles.label}>Sexo</Text>
                <Dropdown options={OPCOES_SEXO} selectedValue={pacienteSexo} onValueChange={setPacienteSexo} />
              </View>
            </View>

            <Text style={styles.subtituloFormulario}>Ancestralidade</Text>
            {ancestralidadeLinhas.map((linha) => (
              <View key={linha.id} style={styles.linhaDinamica}>
                <TextInput
                  style={[styles.inputTexto, styles.inputFlex]}
                  value={linha.origem}
                  onChangeText={(valor) => atualizarAncestralidadeLinha(linha.id, 'origem', valor)}
                  placeholder="Ex: Europa Ibérica"
                  editable={!enviando}
                />
                <TextInput
                  style={[styles.inputTexto, styles.inputPequeno]}
                  value={linha.percentual}
                  onChangeText={(valor) => atualizarAncestralidadeLinha(linha.id, 'percentual', valor)}
                  placeholder="%"
                  keyboardType="numeric"
                  maxLength={3}
                  editable={!enviando}
                />
                <TouchableOpacity
                  style={styles.botaoRemover}
                  onPress={() => removerAncestralidadeLinha(linha.id)}
                  disabled={enviando}
                >
                  <Text style={styles.botaoRemoverTexto}>×</Text>
                </TouchableOpacity>
              </View>
            ))}
            <TouchableOpacity style={styles.linkAdicionar} onPress={adicionarAncestralidadeLinha} disabled={enviando}>
              <Text style={styles.linkAdicionarTexto}>+ Adicionar região</Text>
            </TouchableOpacity>

            <Text style={styles.subtituloFormulario}>Riscos de doenças</Text>
            {riscosLinhas.map((linha) => (
              <View key={linha.id} style={styles.blocoRisco}>
                <View style={styles.campo}>
                  <Text style={styles.label}>Condição</Text>
                  <TextInput
                    style={styles.inputTexto}
                    value={linha.nome}
                    onChangeText={(valor) => atualizarRiscoLinha(linha.id, 'nome', valor)}
                    placeholder="Ex: Diabetes Tipo 2"
                    editable={!enviando}
                  />
                </View>
                <View style={styles.campo}>
                  <Text style={styles.label}>Nível de risco</Text>
                  <Dropdown
                    options={OPCOES_NIVEL_RISCO}
                    selectedValue={linha.nivel}
                    onValueChange={(valor) => atualizarRiscoLinha(linha.id, 'nivel', valor)}
                  />
                </View>
                <View style={styles.campo}>
                  <Text style={styles.label}>Descrição (opcional)</Text>
                  <TextInput
                    style={[styles.inputTexto, styles.inputMultilinha]}
                    value={linha.descricao}
                    onChangeText={(valor) => atualizarRiscoLinha(linha.id, 'descricao', valor)}
                    placeholder="Detalhes do resultado, variantes, recomendações..."
                    multiline
                    editable={!enviando}
                  />
                </View>
                <TouchableOpacity
                  style={styles.linkRemoverRisco}
                  onPress={() => removerRiscoLinha(linha.id)}
                  disabled={enviando}
                >
                  <Text style={styles.linkRemoverRiscoTexto}>Remover</Text>
                </TouchableOpacity>
              </View>
            ))}
            <TouchableOpacity style={styles.linkAdicionar} onPress={adicionarRiscoLinha} disabled={enviando}>
              <Text style={styles.linkAdicionarTexto}>+ Adicionar risco</Text>
            </TouchableOpacity>

            <View style={styles.botoesLinha}>
              <TouchableOpacity style={styles.botaoSecundario} onPress={handleUsarExemplo} disabled={enviando}>
                <Text style={styles.botaoSecundarioTexto}>Usar exemplo</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.botaoPrimario, enviando && styles.botaoDesabilitado]}
                onPress={handleEnviar}
                disabled={enviando}
              >
                <Text style={styles.botaoPrimarioTexto}>{enviando ? 'Enviando...' : 'Enviar relatório'}</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      </View>
    </ScrollView>
  );
}
