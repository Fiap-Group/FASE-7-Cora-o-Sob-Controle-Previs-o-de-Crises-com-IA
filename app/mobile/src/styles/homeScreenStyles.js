import { StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

export default StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20 },
  header: {
    fontSize: 24,
    fontFamily: fonts.extraBold,
    color: colors.textPrimary,
    marginBottom: 20,
  },
});
