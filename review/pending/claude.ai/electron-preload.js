// preload.js - Interface sécurisée entre le renderer et le main process
const { contextBridge, ipcRenderer } = require('electron');

// Exposer les fonctionnalités Claude au renderer process
contextBridge.exposeInMainWorld('claudeAPI', {
  // Gestion des sessions
  listSessions: () => ipcRenderer.invoke('claude:get-sessions'),
  getSession: (sessionId) => ipcRenderer.invoke('claude:get-session', sessionId),
  createSession: () => ipcRenderer.invoke('claude:create-session'),
  
  // Envoi de messages
  sendMessage: (sessionId, message, maxTokens) => 
    ipcRenderer.invoke('claude:send-message', { sessionId, message, maxTokens })
});

// Exposer des utilitaires
contextBridge.exposeInMainWorld('utils', {
  formatDate: (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  }
});
