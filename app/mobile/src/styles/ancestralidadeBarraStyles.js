import { StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

export default StyleSheet.create({
  container: {
    marginBottom: 14,
  },
  linhaTexto: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  regiao: {
    fontSize: 14,
    fontFamily: fonts.regular,
    color: colors.textPrimary,
  },
  percentual: {
    fontSize: 14,
    fontFamily: fonts.bold,
    color: colors.primary,
  },
  trilha: {
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.background,
    overflow: 'hidden',
  },
  barra: {
    height: '100%',
    borderRadius: 4,
    backgroundColor: colors.primary,
  },
});
