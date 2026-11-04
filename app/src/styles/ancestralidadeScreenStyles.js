import { StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

export default StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20 },
  sectionTitle: {
    fontSize: 24,
    fontFamily: fonts.extraBold,
    color: colors.textPrimary,
    marginBottom: 8,
  },
  introducao: {
    fontSize: 13,
    fontFamily: fonts.regular,
    color: colors.textSecondary,
    marginBottom: 20,
    lineHeight: 19,
  },
  section: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  vazioTexto: {
    fontSize: 13,
    fontFamily: fonts.regular,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: 20,
    marginBottom: 20,
    paddingHorizontal: 10,
  },
  linkNovoRelatorio: {
    marginTop: 16,
    alignSelf: 'flex-start',
  },
  linkNovoRelatorioTexto: {
    fontSize: 13,
    fontFamily: fonts.semiBold,
    color: colors.primary,
  },
  linkApagarDados: {
    marginTop: 12,
    alignSelf: 'flex-start',
  },
  linkApagarDadosTexto: {
    fontSize: 13,
    fontFamily: fonts.semiBold,
    color: colors.textSecondary,
    textDecorationLine: 'underline',
  },

  formulario: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginTop: 8,
  },
  tituloFormulario: {
    fontSize: 16,
    fontFamily: fonts.bold,
    color: colors.textPrimary,
    marginBottom: 12,
  },
  subtituloFormulario: {
    fontSize: 13,
    fontFamily: fonts.bold,
    color: colors.textPrimary,
    marginTop: 18,
    marginBottom: 10,
  },
  label: {
    fontSize: 12,
    fontFamily: fonts.semiBold,
    color: colors.textSecondary,
    marginBottom: 6,
  },
  campo: {
    marginBottom: 12,
  },
  linhaDupla: {
    flexDirection: 'row',
    gap: 10,
  },
  campoMetade: {
    flex: 1,
    marginBottom: 12,
  },
  inputTexto: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 13,
    fontFamily: fonts.regular,
    color: colors.textPrimary,
    backgroundColor: colors.background,
  },
  inputMultilinha: {
    minHeight: 60,
    textAlignVertical: 'top',
  },

  linhaDinamica: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  inputFlex: {
    flex: 1,
  },
  inputPequeno: {
    width: 60,
    textAlign: 'center',
  },
  botaoRemover: {
    paddingHorizontal: 6,
    paddingVertical: 4,
  },
  botaoRemoverTexto: {
    fontSize: 18,
    fontFamily: fonts.bold,
    color: colors.status.critical.bg,
  },

  blocoRisco: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    padding: 12,
    marginBottom: 10,
  },
  linkRemoverRisco: {
    alignSelf: 'flex-end',
    marginTop: 4,
  },
  linkRemoverRiscoTexto: {
    fontSize: 12,
    fontFamily: fonts.semiBold,
    color: colors.status.critical.bg,
  },

  linkAdicionar: {
    marginTop: 4,
    marginBottom: 4,
    alignSelf: 'flex-start',
  },
  linkAdicionarTexto: {
    fontSize: 13,
    fontFamily: fonts.semiBold,
    color: colors.primary,
  },

  botoesLinha: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: 10,
    marginTop: 18,
  },
  botaoSecundario: {
    borderWidth: 1,
    borderColor: colors.primary,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  botaoSecundarioTexto: {
    color: colors.primary,
    fontSize: 13,
    fontFamily: fonts.semiBold,
  },
  botaoPrimario: {
    backgroundColor: colors.primary,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  botaoPrimarioTexto: {
    color: colors.white,
    fontSize: 13,
    fontFamily: fonts.semiBold,
  },
  botaoDesabilitado: {
    opacity: 0.5,
  },
});
