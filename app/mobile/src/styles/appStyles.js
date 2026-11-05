import { StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { fonts } from '../theme/typography';

export default StyleSheet.create({
  tabBar: {
    height: 60,
    paddingBottom: 6,
    paddingTop: 6,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  tabBarLabel: { fontSize: 11, fontFamily: fonts.semiBold },
  header: { backgroundColor: colors.primary },
  headerTitle: { fontFamily: fonts.bold, fontSize: 18 },
});
