import { StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

export default StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingBottom: 12,
  },
  titulo: {
    fontSize: 22,
    fontFamily: fonts.extraBold,
    color: colors.textPrimary,
  },
  botaoGerar: {
    backgroundColor: colors.primary,
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  botaoGerarTexto: {
    color: colors.white,
    fontSize: 12,
    fontFamily: fonts.semiBold,
  },
  lista: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  vazio: {
    fontSize: 13,
    fontFamily: fonts.regular,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: 40,
    paddingHorizontal: 30,
  },
});
