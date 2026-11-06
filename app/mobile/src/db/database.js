import * as SQLite from 'expo-sqlite';

const DATABASE_NAME = 'cardioia.db';

let dbPromise = null;

/** Abre (ou reaproveita) a conexão com o banco SQLite local. Guarda a promise (não só o resultado) pra
 * chamadas concorrentes (ex.: App.js e o ThemeProvider abrindo o banco ao mesmo tempo) aguardarem a
 * mesma abertura em vez de chamar `openDatabaseAsync` duas vezes, o que falha no backend web (OPFS). */
function getDatabase() {
  if (!dbPromise) {
    dbPromise = SQLite.openDatabaseAsync(DATABASE_NAME);
  }
  return dbPromise;
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

    CREATE TABLE IF NOT EXISTS avaliacoes_risco (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      criado_em TEXT NOT NULL,
      dados_json TEXT NOT NULL,
      probabilidade REAL NOT NULL,
      classificacao TEXT NOT NULL,
      protocolos_json TEXT NOT NULL,
      recomendacao TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sessao_atual (
      id INTEGER PRIMARY KEY CHECK (id = 1),
      usuario_id INTEGER,
      email TEXT,
      nickname TEXT
    );

    CREATE TABLE IF NOT EXISTS configuracoes (
      chave TEXT PRIMARY KEY,
      valor TEXT NOT NULL
    );
  `);
}

export async function obterConfiguracao(chave) {
  const db = await getDatabase();
  const linha = await db.getFirstAsync('SELECT valor FROM configuracoes WHERE chave = ?', [chave]);
  return linha ? linha.valor : null;
}

export async function salvarConfiguracao(chave, valor) {
  const db = await getDatabase();
  await db.runAsync(
    `INSERT INTO configuracoes (chave, valor) VALUES (?, ?)
     ON CONFLICT (chave) DO UPDATE SET valor = excluded.valor`,
    [chave, valor]
  );
}

export async function definirSessao(usuario) {
  const db = await getDatabase();
  await db.runAsync(
    `INSERT INTO sessao_atual (id, usuario_id, email, nickname) VALUES (1, ?, ?, ?)
     ON CONFLICT (id) DO UPDATE SET usuario_id = excluded.usuario_id, email = excluded.email, nickname = excluded.nickname`,
    [usuario.id, usuario.email, usuario.nickname]
  );
}

export async function encerrarSessao() {
  const db = await getDatabase();
  await db.runAsync('DELETE FROM sessao_atual WHERE id = 1');
}

export async function obterUsuarioLogado() {
  const db = await getDatabase();
  const linha = await db.getFirstAsync('SELECT usuario_id, email, nickname FROM sessao_atual WHERE id = 1');
  return linha ? { id: linha.usuario_id, email: linha.email, nickname: linha.nickname } : null;
}

export async function temConsentimento() {
  const db = await getDatabase();
  const linha = await db.getFirstAsync('SELECT id FROM consentimento LIMIT 1');
  return !!linha;
}

export async function registrarConsentimento() {
  const db = await getDatabase();
  await db.runAsync('INSERT INTO consentimento (aceito_em) VALUES (?)', [new Date().toISOString()]);
}

export async function apagarTodosOsDados() {
  const db = await getDatabase();
  await db.withTransactionAsync(async () => {
    await db.runAsync('DELETE FROM mensagens');
    await db.runAsync('DELETE FROM resumos');
    await db.runAsync('DELETE FROM sessoes_chat');
    await db.runAsync('DELETE FROM perfil_genomico');
    await db.runAsync('DELETE FROM consentimento');
    await db.runAsync('DELETE FROM avaliacoes_risco');
  });
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

export async function deletarResumo(resumoId, sessaoId) {
  const db = await getDatabase();
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

export async function criarAvaliacaoRisco(dadosOperacao, resultado) {
  const db = await getDatabase();
  const agora = new Date().toISOString();
  const inserido = await db.runAsync(
    `INSERT INTO avaliacoes_risco
       (criado_em, dados_json, probabilidade, classificacao, protocolos_json, recomendacao)
     VALUES (?, ?, ?, ?, ?, ?)`,
    [
      agora,
      JSON.stringify(dadosOperacao),
      resultado.probabilidade,
      resultado.classificacao,
      JSON.stringify(resultado.protocolos),
      resultado.recomendacao,
    ]
  );
  return {
    id: inserido.lastInsertRowId,
    criado_em: agora,
    dados: dadosOperacao,
    ...resultado,
  };
}
