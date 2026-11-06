import { StyleSheet } from 'react-native';
import { fonts } from '../theme/typography';

export default function criarEstilos(colors) {
  return StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20 },
  secaoTitulo: {
    fontSize: 14,
    fontFamily: fonts.bold,
    color: colors.textPrimary,
    marginTop: 20,
    marginBottom: 10,
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
  protocolo: {
    fontSize: 13,
    fontFamily: fonts.regular,
    color: colors.textPrimary,
    marginBottom: 8,
    lineHeight: 18,
  },
  });
}
