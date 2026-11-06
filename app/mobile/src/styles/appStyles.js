import { StyleSheet } from 'react-native';
import { fonts } from '../theme/typography';

export default function criarEstilos(colors) {
  return StyleSheet.create({
  tabBar: {
    height: 68,
    paddingBottom: 10,
    paddingTop: 8,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  tabBarLabel: { fontSize: 11, fontFamily: fonts.semiBold, marginTop: 2 },
  header: { backgroundColor: colors.primary },
  headerTitle: { fontFamily: fonts.bold, fontSize: 18 },
  });
}
