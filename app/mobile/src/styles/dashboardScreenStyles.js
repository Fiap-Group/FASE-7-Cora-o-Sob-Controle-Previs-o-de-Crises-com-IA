import { StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

export default StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20 },
  saudacao: {
    fontSize: 24,
    fontFamily: fonts.extraBold,
    color: colors.textPrimary,
  },
  subtitulo: {
    fontSize: 14,
    fontFamily: fonts.regular,
    color: colors.textSecondary,
    marginBottom: 16,
  },
  secao: {
    marginBottom: 24,
  },
  secaoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  secaoTitulo: {
    fontSize: 16,
    fontFamily: fonts.bold,
    color: colors.textPrimary,
  },
  verTudo: {
    fontSize: 13,
    fontFamily: fonts.semiBold,
    color: colors.primary,
  },
  descricaoSecao: {
    fontSize: 13,
    fontFamily: fonts.regular,
    color: colors.textSecondary,
  },
});
