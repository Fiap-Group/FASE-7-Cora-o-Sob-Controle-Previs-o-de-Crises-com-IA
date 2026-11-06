/**
 * Botão deslizante (switch) para alternar entre modo claro e escuro.
 */
export default function AlternadorTema({ tema, onAlternar }) {
  const escuro = tema === 'dark';

  return (
    <button
      type="button"
      role="switch"
      aria-checked={escuro}
      aria-label={escuro ? 'Mudar para modo claro' : 'Mudar para modo escuro'}
      className="alternador-tema"
      onClick={onAlternar}
    >
      <span className="alternador-tema-trilho">
        <span className="alternador-tema-bolinha">
          {escuro ? (
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          ) : (
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="4.5" fill="currentColor" stroke="none" />
              <path d="M12 2v2.5M12 19.5V22M4.93 4.93l1.77 1.77M17.3 17.3l1.77 1.77M2 12h2.5M19.5 12H22M4.93 19.07l1.77-1.77M17.3 6.7l1.77-1.77" />
            </svg>
          )}
        </span>
      </span>
    </button>
  );
}
