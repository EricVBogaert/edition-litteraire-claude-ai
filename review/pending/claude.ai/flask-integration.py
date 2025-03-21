from flask import Flask, request, jsonify
import anthropic
import os
from datetime import datetime

app = Flask(__name__)

# Sessions actives (en mémoire)
active_sessions = {}

# Middleware pour tracer les requêtes
class RequestTracer:
    def __init__(self, func_name):
        self.func_name = func_name
        
    def __call__(self, *args, **kwargs):
        # Enregistrement des infos de début d'appel
        start_time = datetime.now()
        trace_id = f"trace_{start_time.strftime('%Y%m%d%H%M%S')}_{self.func_name}"
        
        print(f"[{trace_id}] DÉBUT - {self.func_name}")
        print(f"[{trace_id}] Args: {args}")
        print(f"[{trace_id}] Kwargs: {kwargs}")
        
        try:
            # Exécution de la fonction
            result = self.func_name(*args, **kwargs)
            
            # Enregistrement des infos de fin d'appel
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"[{trace_id}] FIN - Durée: {duration}s")
            print(f"[{trace_id}] Résultat: {result}")
            
            return result
        except Exception as e:
            # En cas d'erreur
            print(f"[{trace_id}] ERREUR: {str(e)}")
            raise e

# Initialisation du client Claude
@app.before_first_request
def setup_claude():
    app.claude_client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))
    

# Endpoint pour créer une nouvelle session
@app.route('/api/sessions', methods=['POST'])
def create_session():
    session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    active_sessions[session_id] = []
    
    return jsonify({
        "session_id": session_id,
        "message": "Session créée avec succès"
    })

# Endpoint pour envoyer un message dans une session
@app.route('/api/sessions/<session_id>/messages', methods=['POST'])
@RequestTracer
def send_message(session_id):
    if session_id not in active_sessions:
        return jsonify({"error": "Session non trouvée"}), 404
    
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Message requis"}), 400
    
    # Ajouter le message utilisateur à l'historique
    active_sessions[session_id].append({
        "role": "user",
        "content": data['message']
    })
    
    # Appel à l'API Claude avec l'historique complet
    response = app.claude_client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=data.get('max_tokens', 1000),
        messages=active_sessions[session_id]
    )
    
    # Extraire la réponse
    assistant_message = response.content[0].text
    
    # Ajouter la réponse à l'historique
    active_sessions[session_id].append({
        "role": "assistant",
        "content": assistant_message
    })
    
    return jsonify({
        "message": assistant_message,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    })

# Endpoint pour récupérer l'historique d'une session
@app.route('/api/sessions/<session_id>/history', methods=['GET'])
def get_session_history(session_id):
    if session_id not in active_sessions:
        return jsonify({"error": "Session non trouvée"}), 404
    
    return jsonify({
        "session_id": session_id,
        "history": active_sessions[session_id]
    })

# Lancement de l'application
if __name__ == '__main__':
    app.run(debug=True)
