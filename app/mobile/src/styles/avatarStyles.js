import { StyleSheet } from 'react-native';
import { fonts } from '../theme/typography';

export default function criarEstilos(colors) {
  return StyleSheet.create({
  circulo: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  inicial: {
    color: colors.white,
    fontFamily: fonts.extraBold,
  },
  });
}
