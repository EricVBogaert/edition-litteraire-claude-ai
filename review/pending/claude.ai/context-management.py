import anthropic
import json
from datetime import datetime

class ClaudeSession:
    def __init__(self, api_key, model="claude-3-7-sonnet-20250219", session_id=None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.conversation_history = []
        
    def add_message(self, role, content):
        """Ajoute un message à l'historique de conversation"""
        self.conversation_history.append({"role": role, "content": content})
        
    def get_response(self, prompt, max_tokens=1000):
        """Obtient une réponse de Claude en tenant compte du contexte"""
        # Ajouter le message utilisateur à l'historique
        self.add_message("user", prompt)
        
        # Créer la requête avec l'historique complet
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=self.conversation_history
        )
        
        # Ajouter la réponse à l'historique
        response_text = message.content[0].text
        self.add_message("assistant", response_text)
        
        return response_text
        
    def save_session(self, file_path=None):
        """Sauvegarde la session dans un fichier JSON"""
        file_path = file_path or f"{self.session_id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": self.session_id,
                "model": self.model,
                "conversation_history": self.conversation_history
            }, f, ensure_ascii=False, indent=2)
            
        return file_path
        
    @classmethod
    def load_session(cls, file_path, api_key):
        """Charge une session depuis un fichier JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        session = cls(api_key, data.get("model", "claude-3-7-sonnet-20250219"), data.get("session_id"))
        session.conversation_history = data.get("conversation_history", [])
        
        return session

# Exemple d'utilisation
def demo_session():
    api_key = "votre_clé_api"
    
    # Création d'une nouvelle session
    session = ClaudeSession(api_key)
    
    # Premier échange
    response1 = session.get_response("Bonjour Claude, peux-tu te présenter?")
    print("Réponse 1:", response1)
    
    # Deuxième échange (avec contexte)
    response2 = session.get_response("Quelles sont tes capacités principales?")
    print("Réponse 2:", response2)
    
    # Sauvegarde de la session
    saved_path = session.save_session()
    print(f"Session sauvegardée dans {saved_path}")
    
    # Plus tard, chargement de la session
    loaded_session = ClaudeSession.load_session(saved_path, api_key)
    
    # Continuation de la conversation
    response3 = loaded_session.get_response("Peux-tu me donner un exemple de code Python?")
    print("Réponse 3:", response3)
