import { StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

export default StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
    paddingTop: 14,
    paddingBottom: 36,
    paddingHorizontal: 16,
    marginBottom: 12,
    position: 'relative',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  conteudoClicavel: {},
  titulo: {
    fontSize: 12,
    fontFamily: fonts.semiBold,
    color: colors.primary,
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  data: {
    fontSize: 16,
    fontFamily: fonts.bold,
    color: colors.textPrimary,
  },
  botaoRemover: {
    position: 'absolute',
    bottom: 8,
    right: 10,
    padding: 4,
  },
  iconeRemover: {
    fontSize: 16,
  },
});
