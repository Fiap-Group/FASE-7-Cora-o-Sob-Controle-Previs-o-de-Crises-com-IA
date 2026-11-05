import { useState } from 'react';
import { Modal, Pressable, Text, TouchableOpacity, View } from 'react-native';
import styles from '../styles/dropdownStyles';

export default function Dropdown({ options, selectedValue, onValueChange }) {
  const [aberto, setAberto] = useState(false);

  const opcaoSelecionada = options.find((opcao) => opcao.value === selectedValue);

  const handleSelecionar = (valor) => {
    onValueChange(valor);
    setAberto(false);
  };

  return (
    <View>
      <TouchableOpacity style={styles.trigger} onPress={() => setAberto(true)}>
        <Text style={styles.triggerTexto}>{opcaoSelecionada?.label}</Text>
        <Text style={styles.seta}>▾</Text>
      </TouchableOpacity>

      <Modal visible={aberto} transparent animationType="fade" onRequestClose={() => setAberto(false)}>
        <Pressable style={styles.overlay} onPress={() => setAberto(false)}>
          <View style={styles.painel}>
            {options.map((opcao) => (
              <TouchableOpacity
                key={opcao.value}
                style={[styles.opcao, opcao.value === selectedValue && styles.opcaoSelecionada]}
                onPress={() => handleSelecionar(opcao.value)}
              >
                <Text
                  style={[styles.opcaoTexto, opcao.value === selectedValue && styles.opcaoTextoSelecionado]}
                >
                  {opcao.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </Pressable>
      </Modal>
    </View>
  );
}
