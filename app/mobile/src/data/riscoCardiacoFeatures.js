// As 10 features que o backend espera para prever o risco de crise cardíaca
// (ver app/backend/shared/preditivo/dataset.py:COLUNAS_FEATURES). As chaves
// aqui precisam ser idênticas às de lá — é o contrato entre front e backend.
export const RISCO_CARDIACO_FEATURES = [
  { chave: 'idade_media', label: 'Idade média dos pacientes', unidade: 'anos', exemplo: 60 },
  { chave: 'carga_sistema', label: 'Carga do sistema', unidade: '%', exemplo: 90 },
  { chave: 'tempo_espera', label: 'Tempo médio de espera', unidade: 'min', exemplo: 100 },
  { chave: 'fc_media', label: 'Frequência cardíaca média', unidade: 'bpm', exemplo: 125 },
  { chave: 'spo2_media', label: 'SPO2 médio', unidade: '%', exemplo: 85 },
  { chave: 'pa_sistolica', label: 'Pressão arterial sistólica média', unidade: 'mmHg', exemplo: 85 },
  { chave: 'temperatura', label: 'Temperatura média', unidade: '°C', exemplo: 39 },
  { chave: 'densidade_eventos', label: 'Densidade de eventos', unidade: 'eventos/período', exemplo: 7 },
  { chave: 'eventos_24h', label: 'Eventos nas últimas 24h', unidade: 'eventos', exemplo: 6 },
  { chave: 'disponibilidade_recursos', label: 'Disponibilidade de recursos', unidade: '%', exemplo: 20 },
];
