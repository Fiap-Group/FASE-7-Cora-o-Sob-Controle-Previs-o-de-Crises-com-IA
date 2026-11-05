import { StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

// Mesmo vocabulário visual de ancestralidadeScreenStyles.js (formulario,
// campo, inputTexto, botaoPrimario) — compartilhado por Login, Cadastro
// e EscolherNickname.
export default StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20, flexGrow: 1, justifyContent: 'center' },
  titulo: {
    fontSize: 24,
    fontFamily: fonts.extraBold,
    color: colors.textPrimary,
    marginBottom: 8,
    textAlign: 'center',
  },
  introducao: {
    fontSize: 13,
    fontFamily: fonts.regular,
    color: colors.textSecondary,
    marginBottom: 24,
    textAlign: 'center',
  },
  formulario: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
  },
  campo: { marginBottom: 12 },
  label: {
    fontSize: 12,
    fontFamily: fonts.semiBold,
    color: colors.textSecondary,
    marginBottom: 6,
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
  botaoPrimario: {
    backgroundColor: colors.primary,
    borderRadius: 20,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  botaoPrimarioTexto: {
    color: colors.white,
    fontSize: 14,
    fontFamily: fonts.semiBold,
  },
  botaoDesabilitado: { opacity: 0.5 },
  erroTexto: {
    fontSize: 12,
    fontFamily: fonts.regular,
    color: colors.status.critical.bg,
    marginTop: 4,
  },
  linkAlternar: { marginTop: 18, alignItems: 'center' },
  linkAlternarTexto: {
    fontSize: 13,
    fontFamily: fonts.semiBold,
    color: colors.primary,
  },
});
