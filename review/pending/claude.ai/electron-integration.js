// main.js - Point d'entrée pour Electron
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { Anthropic } = require('@anthropic-ai/sdk');
const fs = require('fs').promises;

// Configuration
const CONFIG = {
  apiKey: process.env.CLAUDE_API_KEY || "",
  model: "claude-3-7-sonnet-20250219",
  sessionsPath: path.join(app.getPath('userData'), 'sessions')
};

// Initialisation du client Claude
const claude = new Anthropic({
  apiKey: CONFIG.apiKey,
});

// Création de la fenêtre principale
function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile('index.html');
}

// Gestion des sessions
const SessionManager = {
  async ensureSessionsDir() {
    try {
      await fs.mkdir(CONFIG.sessionsPath, { recursive: true });
    } catch (err) {
      console.error("Erreur lors de la création du dossier sessions:", err);
    }
  },

  async loadSession(sessionId) {
    try {
      const filePath = path.join(CONFIG.sessionsPath, `${sessionId}.json`);
      const data = await fs.readFile(filePath, 'utf8');
      return JSON.parse(data);
    } catch (err) {
      console.error(`Erreur lors du chargement de la session ${sessionId}:`, err);
      return null;
    }
  },

  async saveSession(sessionId, data) {
    try {
      await this.ensureSessionsDir();
      const filePath = path.join(CONFIG.sessionsPath, `${sessionId}.json`);
      await fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');
      return true;
    } catch (err) {
      console.error(`Erreur lors de la sauvegarde de la session ${sessionId}:`, err);
      return false;
    }
  },

  async listSessions() {
    try {
      await this.ensureSessionsDir();
      const files = await fs.readdir(CONFIG.sessionsPath);
      return files
        .filter(file => file.endsWith('.json'))
        .map(file => file.replace('.json', ''));
    } catch (err) {
      console.error("Erreur lors de la liste des sessions:", err);
      return [];
    }
  }
};

// Gestion des IPC (communication entre processus)
ipcMain.handle('claude:send-message', async (event, { sessionId, message, maxTokens = 1000 }) => {
  try {
    // Charger la session ou en créer une nouvelle
    let session = await SessionManager.loadSession(sessionId);
    if (!session) {
      session = {
        id: sessionId,
        createdAt: new Date().toISOString(),
        messages: []
      };
    }

    // Ajouter le message utilisateur
    session.messages.push({
      role: "user",
      content: message
    });

    // Appeler Claude
    const response = await claude.messages.create({
      model: CONFIG.model,
      max_tokens: maxTokens,
      messages: session.messages.map(m => ({
        role: m.role,
        content: m.content
      }))
    });

    // Extraire la réponse
    const assistantMessage = response.content[0].text;

    // Ajouter la réponse à l'historique
    session.messages.push({
      role: "assistant",
      content: assistantMessage
    });

    // Sauvegarder la session mise à jour
    await SessionManager.saveSession(sessionId, session);

    return {
      message: assistantMessage,
      usage: {
        inputTokens: response.usage.input_tokens,
        outputTokens: response.usage.output_tokens
      }
    };
  } catch (err) {
    console.error("Erreur lors de l'envoi du message:", err);
    throw err;
  }
});

ipcMain.handle('claude:get-sessions', async () => {
  return await SessionManager.listSessions();
});

ipcMain.handle('claude:get-session', async (event, sessionId) => {
  return await SessionManager.loadSession(sessionId);
});

ipcMain.handle('claude:create-session', async () => {
  const sessionId = `session_${Date.now()}`;
  const session = {
    id: sessionId,
    createdAt: new Date().toISOString(),
    messages: []
  };
  await SessionManager.saveSession(sessionId, session);
  return sessionId;
});

// Initialisation de l'application
app.whenReady().then(async () => {
  await SessionManager.ensureSessionsDir();
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
