import { StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

export default StyleSheet.create({
  container: {
    flex: 1,
  },
  lista: {
    padding: 16,
    paddingBottom: 8,
  },
  bolha: {
    maxWidth: '80%',
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 10,
    marginBottom: 10,
  },
  bolhaUsuario: {
    alignSelf: 'flex-end',
    backgroundColor: colors.primary,
    borderBottomRightRadius: 4,
  },
  bolhaIA: {
    alignSelf: 'flex-start',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderBottomLeftRadius: 4,
  },
  textoUsuario: {
    fontSize: 14,
    fontFamily: fonts.regular,
    color: colors.white,
  },
  textoIA: {
    fontSize: 14,
    fontFamily: fonts.regular,
    color: colors.textPrimary,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 12,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    backgroundColor: colors.surface,
  },
  input: {
    flex: 1,
    maxHeight: 100,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 14,
    fontFamily: fonts.regular,
    color: colors.textPrimary,
    marginRight: 8,
  },
  enviarBotao: {
    backgroundColor: colors.primary,
    borderRadius: 20,
    paddingHorizontal: 18,
    paddingVertical: 12,
  },
  enviarBotaoDesabilitado: {
    backgroundColor: colors.textMuted,
  },
  enviarTexto: {
    color: colors.white,
    fontSize: 14,
    fontFamily: fonts.semiBold,
  },
  blocoFontes: {
    marginTop: -4,
    marginBottom: 12,
    paddingHorizontal: 4,
  },
  fontesTitulo: {
    fontSize: 12,
    fontFamily: fonts.semiBold,
    color: colors.textSecondary,
    paddingVertical: 4,
  },
  fonteItem: {
    fontSize: 12,
    fontFamily: fonts.regular,
    color: colors.textSecondary,
    lineHeight: 17,
    marginBottom: 6,
    paddingLeft: 8,
  },
  fonteSecao: {
    fontFamily: fonts.semiBold,
    color: colors.textPrimary,
  },
});
