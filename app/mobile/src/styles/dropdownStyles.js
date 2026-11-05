import { StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

export default StyleSheet.create({
  trigger: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 24,
    paddingHorizontal: 16,
    height: 48,
  },
  triggerTexto: {
    fontSize: 14,
    fontFamily: fonts.regular,
    color: colors.textPrimary,
  },
  seta: {
    fontSize: 14,
    color: colors.textMuted,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    justifyContent: 'center',
    padding: 32,
  },
  painel: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    paddingVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 6,
  },
  opcao: {
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 16,
    marginHorizontal: 8,
  },
  opcaoSelecionada: {
    backgroundColor: colors.background,
  },
  opcaoTexto: {
    fontSize: 15,
    fontFamily: fonts.regular,
    color: colors.textPrimary,
  },
  opcaoTextoSelecionado: {
    fontFamily: fonts.bold,
    color: colors.primary,
  },
});
