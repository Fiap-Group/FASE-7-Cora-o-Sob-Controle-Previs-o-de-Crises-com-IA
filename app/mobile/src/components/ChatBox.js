import { useEffect, useRef, useState } from 'react';
import { FlatList, KeyboardAvoidingView, Platform, Text, TextInput, TouchableOpacity, View } from 'react-native';
import { colors } from '../theme/colors';
import { buscarMensagens, salvarMensagem } from '../db/database';
import { perguntarAoAgente } from '../services/api';
import styles from '../styles/chatBoxStyles';

const NOMES_SECAO = {
  perfil: 'Seu perfil',
  ancestralidade: 'Sua ancestralidade',
  riscos_doencas: 'Riscos de doenças',
  bem_estar: 'Bem-estar e medicamentos',
  recomendacoes: 'Recomendações',
};

/** Caixa de chat que exibe o histórico de mensagens e permite conversar com o agente de IA. */
export default function ChatBox({ sessaoId }) {
  const [mensagens, setMensagens] = useState([]);
  const [texto, setTexto] = useState('');
  const [fontesAbertas, setFontesAbertas] = useState({});
  const listaRef = useRef(null);

  useEffect(() => {
    if (!sessaoId) return;

    (async () => {
      const historico = await buscarMensagens(sessaoId);
      setMensagens(historico.map((item) => ({ id: String(item.id), autor: item.autor, texto: item.texto })));
    })();
  }, [sessaoId]);

  /** Envia a mensagem digitada ao agente e atualiza o histórico com a resposta. */
  const handleEnviar = async () => {
    const mensagemDigitada = texto.trim();
    if (!mensagemDigitada || !sessaoId) return;

    const mensagemUsuario = { id: Date.now().toString(), autor: 'usuario', texto: mensagemDigitada };
    setMensagens((atual) => [...atual, mensagemUsuario]);
    setTexto('');
    await salvarMensagem(sessaoId, 'usuario', mensagemDigitada);

    try {
      const resultado = await perguntarAoAgente(mensagemDigitada);
      const respostaIA = {
        id: (Date.now() + 1).toString(),
        autor: 'ia',
        texto: resultado.answer,
        fontes: resultado.sources || [],
      };
      setMensagens((atual) => [...atual, respostaIA]);
      await salvarMensagem(sessaoId, 'ia', resultado.answer);
    } catch (erro) {
      const semRelatorio = erro.message?.startsWith('Nenhum relatório enviado');
      const textoErro = semRelatorio
        ? erro.message
        : 'Não consegui falar com o agente agora. Verifique se o backend está rodando e se a chave de ' +
          `API foi configurada. Detalhe: ${erro.message}`;
      const respostaErro = { id: (Date.now() + 1).toString(), autor: 'ia', texto: textoErro };
      setMensagens((atual) => [...atual, respostaErro]);
      await salvarMensagem(sessaoId, 'ia', textoErro);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      <FlatList
        ref={listaRef}
        data={mensagens}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.lista}
        onContentSizeChange={() => listaRef.current?.scrollToEnd({ animated: true })}
        renderItem={({ item }) => (
          <View>
            <View style={[styles.bolha, item.autor === 'usuario' ? styles.bolhaUsuario : styles.bolhaIA]}>
              <Text style={item.autor === 'usuario' ? styles.textoUsuario : styles.textoIA}>{item.texto}</Text>
            </View>

            {item.fontes?.length > 0 && (
              <View style={styles.blocoFontes}>
                <TouchableOpacity
                  onPress={() => setFontesAbertas((atual) => ({ ...atual, [item.id]: !atual[item.id] }))}
                >
                  <Text style={styles.fontesTitulo}>
                    {fontesAbertas[item.id] ? '▾' : '▸'} Fontes consultadas no seu relatório ({item.fontes.length})
                  </Text>
                </TouchableOpacity>

                {fontesAbertas[item.id] &&
                  item.fontes.map((fonte, indice) => (
                    <Text key={`${item.id}-${indice}`} style={styles.fonteItem}>
                      <Text style={styles.fonteSecao}>{NOMES_SECAO[fonte.section] || fonte.section}: </Text>
                      {fonte.text.length > 180 ? `${fonte.text.slice(0, 180)}…` : fonte.text}
                    </Text>
                  ))}
              </View>
            )}
          </View>
        )}
      />

      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          value={texto}
          onChangeText={setTexto}
          placeholder="Digite sua pergunta..."
          placeholderTextColor={colors.textMuted}
          multiline
        />
        <TouchableOpacity
          style={[styles.enviarBotao, !texto.trim() && styles.enviarBotaoDesabilitado]}
          onPress={handleEnviar}
          disabled={!texto.trim()}
        >
          <Text style={styles.enviarTexto}>Enviar</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}
