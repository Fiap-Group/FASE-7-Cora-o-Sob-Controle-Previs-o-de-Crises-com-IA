import os


def ler_chaves_gemini() -> list[str]:
    """Lê uma ou mais chaves de API do Gemini do .env.

    GEMINI_API_KEYS aceita várias chaves separadas por vírgula (uma por conta Google — por
    exemplo, uma por integrante da equipe). GEMINI_API_KEY/GOOGLE_API_KEY seguem funcionando
    como alternativa de uma chave só. A cota gratuita é por conta Google, não por chave, então
    ter mais de uma chave configurada permite trocar de conta quando uma esgota a cota do dia.
    """
    bruto = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    chaves = [chave.strip() for chave in bruto.split(",") if chave.strip()]
    if not chaves:
        raise RuntimeError(
            "Nenhuma chave de API do Gemini definida — defina GEMINI_API_KEYS (uma ou mais, "
            "separadas por vírgula) ou GEMINI_API_KEY no .env (ver app/backend/.env.example)."
        )
    return chaves
