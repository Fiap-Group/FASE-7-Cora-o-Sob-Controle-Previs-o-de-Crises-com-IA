import { StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

export default StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: {
    padding: 12,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  headerTexto: {
    fontSize: 12,
    fontFamily: fonts.regular,
    color: colors.textSecondary,
  },
});
