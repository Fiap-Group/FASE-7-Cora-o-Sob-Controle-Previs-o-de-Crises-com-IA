from shared.preditivo.dataset import gerar_base_sintetica
from shared.preditivo.modelo import salvar_modelo, treinar_modelo


def main() -> None:
    """Gera a base sintética, treina o modelo, imprime as métricas e salva o checkpoint."""
    print("Gerando base sintética (5000 pacientes)...")
    df = gerar_base_sintetica(n=5000, seed=42)
    print(f"Distribuição de pico_risco:\n{df['pico_risco'].value_counts()}\n")

    print("Treinando a rede (PyTorch)...")
    modelo, scaler_mean, scaler_scale, metricas = treinar_modelo(df, seed=42)

    print(f"\nAcurácia: {metricas['acuracia']:.2%}")
    print(f"\nMatriz de confusão:\n{metricas['matriz_confusao']}")
    print(f"\nRelatório de classificação:")
    relatorio = metricas["relatorio"]
    for classe in ("0", "1"):
        linha = relatorio[classe]
        print(
            f"  classe {classe}: precision={linha['precision']:.2f} "
            f"recall={linha['recall']:.2f} f1={linha['f1-score']:.2f}"
        )

    print(
        "\nNota: a acurácia alta aqui é esperada — pico_risco é função "
        "determinística das próprias features de treino (ver dataset.py). "
        "Não é vazamento de dados, é a natureza da base sintética do enunciado."
    )

    salvar_modelo(modelo, scaler_mean, scaler_scale)
    print("\nModelo salvo com sucesso!")


if __name__ == "__main__":
    main()
