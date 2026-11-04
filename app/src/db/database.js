import * as SQLite from 'expo-sqlite';

const DATABASE_NAME = 'dasa.db';

let dbInstance = null;

async function getDatabase() {
  if (!dbInstance) {
    dbInstance = await SQLite.openDatabaseAsync(DATABASE_NAME);
  }
  return dbInstance;
}

export async function initDatabase() {
  const db = await getDatabase();
  await db.execAsync(`
    PRAGMA journal_mode = WAL;

    CREATE TABLE IF NOT EXISTS sessoes_chat (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      criado_em TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS mensagens (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      sessao_id INTEGER NOT NULL,
      autor TEXT NOT NULL,
      texto TEXT NOT NULL,
      criado_em TEXT NOT NULL,
      FOREIGN KEY (sessao_id) REFERENCES sessoes_chat(id)
    );

    CREATE TABLE IF NOT EXISTS resumos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      data_criacao TEXT NOT NULL,
      conteudo TEXT NOT NULL,
      sessao_id INTEGER NOT NULL,
      FOREIGN KEY (sessao_id) REFERENCES sessoes_chat(id)
    );

    CREATE TABLE IF NOT EXISTS perfil_genomico (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      criado_em TEXT NOT NULL,
      dados_json TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS consentimento (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      aceito_em TEXT NOT NULL
    );
  `);
}

// Consentimento LGPD: registro de que a pessoa autorizou o uso dos dados
// do relatório (dado de saúde, Art. 11). Só o primeiro aceite é gravado.
export async function temConsentimento() {
  const db = await getDatabase();
  const linha = await db.getFirstAsync('SELECT id FROM consentimento LIMIT 1');
  return !!linha;
}

export async function registrarConsentimento() {
  const db = await getDatabase();
  await db.runAsync('INSERT INTO consentimento (aceito_em) VALUES (?)', [new Date().toISOString()]);
}

// "Apagar meus dados" (LGPD, direito de eliminação): remove do dispositivo
// todos os registros pessoais e o consentimento, em uma única transação.
export async function apagarTodosOsDados() {
  const db = await getDatabase();
  await db.withTransactionAsync(async () => {
    await db.runAsync('DELETE FROM mensagens');
    await db.runAsync('DELETE FROM resumos');
    await db.runAsync('DELETE FROM sessoes_chat');
    await db.runAsync('DELETE FROM perfil_genomico');
    await db.runAsync('DELETE FROM consentimento');
  });
}

export async function obterSessaoAtual() {
  const db = await getDatabase();
  const sessaoExistente = await db.getFirstAsync(
    'SELECT id FROM sessoes_chat ORDER BY id DESC LIMIT 1'
  );

  if (sessaoExistente) {
    return sessaoExistente.id;
  }

  const resultado = await db.runAsync(
    'INSERT INTO sessoes_chat (criado_em) VALUES (?)',
    [new Date().toISOString()]
  );
  return resultado.lastInsertRowId;
}

export async function salvarMensagem(sessaoId, autor, texto) {
  const db = await getDatabase();
  await db.runAsync(
    'INSERT INTO mensagens (sessao_id, autor, texto, criado_em) VALUES (?, ?, ?, ?)',
    [sessaoId, autor, texto, new Date().toISOString()]
  );
}

export async function buscarMensagens(sessaoId) {
  const db = await getDatabase();
  return db.getAllAsync(
    'SELECT id, autor, texto, criado_em FROM mensagens WHERE sessao_id = ? ORDER BY id ASC',
    [sessaoId]
  );
}

// Cria um novo resumo: abre uma sessão de chat própria pra ele e já grava
// o conteúdo do resumo como a primeira mensagem (autor 'ia') dessa sessão.
export async function criarResumo(conteudo) {
  const db = await getDatabase();
  const agora = new Date().toISOString();

  const sessao = await db.runAsync('INSERT INTO sessoes_chat (criado_em) VALUES (?)', [agora]);
  const sessaoId = sessao.lastInsertRowId;

  await db.runAsync(
    'INSERT INTO mensagens (sessao_id, autor, texto, criado_em) VALUES (?, ?, ?, ?)',
    [sessaoId, 'ia', conteudo, agora]
  );

  const resumo = await db.runAsync(
    'INSERT INTO resumos (data_criacao, conteudo, sessao_id) VALUES (?, ?, ?)',
    [agora, conteudo, sessaoId]
  );

  return { id: resumo.lastInsertRowId, data_criacao: agora, conteudo, sessao_id: sessaoId };
}

export async function buscarResumos() {
  const db = await getDatabase();
  return db.getAllAsync(
    'SELECT id, data_criacao, conteudo, sessao_id FROM resumos ORDER BY id DESC'
  );
}

// Remove o resumo e toda a conversa (mensagens + sessão) associada a ele,
// já que cada resumo é dono de uma sessão de chat própria (ver criarResumo).
export async function deletarResumo(resumoId, sessaoId) {
  const db = await getDatabase();
  // Transação: se um dos DELETEs falhar, nenhum é aplicado (sem mensagens órfãs).
  await db.withTransactionAsync(async () => {
    await db.runAsync('DELETE FROM mensagens WHERE sessao_id = ?', [sessaoId]);
    await db.runAsync('DELETE FROM resumos WHERE id = ?', [resumoId]);
    await db.runAsync('DELETE FROM sessoes_chat WHERE id = ?', [sessaoId]);
  });
}

export async function salvarPerfilGenomico(objetoJson) {
  const db = await getDatabase();
  const agora = new Date().toISOString();
  const resultado = await db.runAsync(
    'INSERT INTO perfil_genomico (criado_em, dados_json) VALUES (?, ?)',
    [agora, JSON.stringify(objetoJson)]
  );
  return { id: resultado.lastInsertRowId, criado_em: agora };
}

export async function buscarPerfilGenomicoAtual() {
  const db = await getDatabase();
  const linha = await db.getFirstAsync(
    'SELECT dados_json FROM perfil_genomico ORDER BY id DESC LIMIT 1'
  );
  return linha ? JSON.parse(linha.dados_json) : null;
}
