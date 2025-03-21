import time
import json
import logging
import inspect
import functools
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Callable, Optional

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("claude_api_traces.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("claude_dispatcher")

class FunctionTracer:
    """
    Décorateur pour tracer les appels de fonction avec leur contexte,
    paramètres et résultats
    """
    
    def __init__(self, category: str = "default"):
        self.category = category
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Génération d'un identifiant unique pour l'appel
            trace_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Récupération des informations sur l'appelant
            caller_frame = inspect.currentframe().f_back
            caller_info = {
                "file": caller_frame.f_code.co_filename,
                "line": caller_frame.f_lineno,
                "function": caller_frame.f_code.co_name
            }
            
            # Préparation des informations sur l'appel
            call_info = {
                "trace_id": trace_id,
                "timestamp": datetime.now().isoformat(),
                "category": self.category,
                "function": func.__name__,
                "module": func.__module__,
                "caller": caller_info,
                "args": [self._sanitize_arg(arg) for arg in args],
                "kwargs": {k: self._sanitize_arg(v) for k, v in kwargs.items()},
                "start_time": start_time
            }
            
            # Journalisation du début de l'appel
            logger.info(f"DÉBUT APPEL [{trace_id}]: {func.__name__}")
            
            try:
                # Exécution de la fonction
                result = func(*args, **kwargs)
                
                # Calcul de la durée
                end_time = time.time()
                duration = end_time - start_time
                
                # Mise à jour des informations avec le résultat
                call_info.update({
                    "status": "success",
                    "duration": duration,
                    "end_time": end_time,
                    "result": self._sanitize_arg(result)
                })
                
                # Journalisation de la fin de l'appel
                logger.info(f"FIN APPEL [{trace_id}]: {func.__name__} ({duration:.4f}s)")
                
                # Enregistrement détaillé de l'appel
                self._save_trace(call_info)
                
                return result
            except Exception as e:
                # En cas d'erreur
                end_time = time.time()
                duration = end_time - start_time
                
                # Mise à jour des informations avec l'erreur
                call_info.update({
                    "status": "error",
                    "duration": duration,
                    "end_time": end_time,
                    "error": {
                        "type": type(e).__name__,
                        "message": str(e)
                    }
                })
                
                # Journalisation de l'erreur
                logger.error(f"ERREUR APPEL [{trace_id}]: {func.__name__} - {str(e)}")
                
                # Enregistrement détaillé de l'appel avec erreur
                self._save_trace(call_info)
                
                # Relancer l'exception
                raise
        
        return wrapper
    
    def _sanitize_arg(self, arg: Any) -> Any:
        """
        Sanitize argument values for logging (avoid sensitive data)
        """
        # Stratégie simple pour masquer les clés API
        if isinstance(arg, str) and (
            arg.startswith("sk-") or 
            arg.startswith("apikey-") or
            len(arg) > 20 and any(s in arg.lower() for s in ["key", "secret", "password", "token"])
        ):
            return "***REDACTED***"
        
        # Pour les objets complexes, retourner leur représentation ou type
        if not isinstance(arg, (str, int, float, bool, type(None))):
            try:
                # Tenter une représentation JSON pour les dictionnaires/listes
                if isinstance(arg, (dict, list)):
                    # Limiter la taille pour éviter des logs trop volumineux
                    json_str = json.dumps(arg)
                    if len(json_str) > 1000:
                        if isinstance(arg, dict):
                            return {"__type": "dict", "keys": list(arg.keys()), "length": len(arg)}
                        else:
                            return {"__type": "list", "length": len(arg)}
                    return arg
                return str(arg)
            except:
                return {"__type": type(arg).__name__}
        
        return arg
    
    def _save_trace(self, trace_info: Dict) -> None:
        """
        Sauvegarde les informations d'un appel dans un fichier JSON
        """
        # Créer le dossier de traces s'il n'existe pas
        traces_dir = os.path.join(os.getcwd(), "traces")
        os.makedirs(traces_dir, exist_ok=True)
        
        # Générer le nom de fichier basé sur l'ID de trace
        trace_file = os.path.join(traces_dir, f"trace_{trace_info['trace_id']}.json")
        
        # Écrire les informations dans le fichier
        with open(trace_file, 'w', encoding='utf-8') as f:
            json.dump(trace_info, f, ensure_ascii=False, indent=2, default=str)


class ClaudeDispatcher:
    """
    Dispatcher central pour les appels à l'API Claude.ai
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.active_sessions = {}
    
    @FunctionTracer(category="session")
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Crée une nouvelle session Claude
        """
        from anthropic import Anthropic
        
        # Générer un ID de session si non fourni
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Initialiser le client et la session
        client = Anthropic(api_key=self.api_key)
        
        # Stocker la session
        self.active_sessions[session_id] = {
            "client": client,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        
        return session_id
    
    @FunctionTracer(category="message")
    def send_message(self, session_id: str, message: str, 
                    max_tokens: int = 1000, model: str = "claude-3-7-sonnet-20250219") -> Dict:
        """
        Envoie un message à Claude dans une session spécifique
        """
        # Vérifier si la session existe
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} non trouvée")
        
        session = self.active_sessions[session_id]
        client = session["client"]
        
        # Ajouter le message utilisateur à l'historique
        session["messages"].append({
            "role": "user",
            "content": message
        })
        
        # Appeler l'API Claude
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=session["messages"]
        )
        
        # Extraire la réponse
        assistant_message = response.content[0].text
        
        # Ajouter la réponse à l'historique
        session["messages"].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Retourner la réponse et les informations d'utilisation
        return {
            "message": assistant_message,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }
    
    @FunctionTracer(category="session")
    def get_session_history(self, session_id: str) -> List:
        """
        Récupère l'historique des messages d'une session
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} non trouvée")
        
        return self.active_sessions[session_id]["messages"]
    
    @FunctionTracer(category="session")
    def save_session(self, session_id: str, file_path: Optional[str] = None) -> str:
        """
        Sauvegarde une session dans un fichier JSON
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} non trouvée")
        
        session = self.active_sessions[session_id]
        
        # Générer le chemin du fichier si non fourni
        if not file_path:
            sessions_dir = os.path.join(os.getcwd(), "sessions")
            os.makedirs(sessions_dir, exist_ok=True)
            file_path = os.path.join(sessions_dir, f"{session_id}.json")
        
        # Extraire les données pertinentes (sans le client)
        save_data = {
            "session_id": session_id,
            "created_at": session["created_at"],
            "messages": session["messages"]
        }
        
        # Sauvegarder dans un fichier JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    @FunctionTracer(category="session")
    def load_session(self, file_path: str) -> str:
        """
        Charge une session depuis un fichier JSON
        """
        # Lire le fichier JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        session_id = data["session_id"]
        
        # Créer une nouvelle session avec les données chargées
        self.create_session(session_id)
        
        # Mettre à jour les données de la session
        self.active_sessions[session_id].update({
            "created_at": data["created_at"],
            "messages": data["messages"]
        })
        
        return session_id


# Exemple d'utilisation
def demo_claude_dispatcher():
    # Initialiser le dispatcher
    dispatcher = ClaudeDispatcher(api_key="votre_clé_api")
    
    # Créer une session
    session_id = dispatcher.create_session()
    print(f"Session créée: {session_id}")
    
    # Envoyer un premier message
    response1 = dispatcher.send_message(
        session_id=session_id,
        message="Bonjour Claude, peux-tu te présenter?"
    )
    print(f"Réponse: {response1['message']}")
    print(f"Tokens utilisés: {response1['usage']}")
    
    # Envoyer un second message (avec contexte)
    response2 = dispatcher.send_message(
        session_id=session_id,
        message="Quelles sont tes capacités principales?"
    )
    print(f"Réponse: {response2['message']}")
    
    # Sauvegarder la session
    save_path = dispatcher.save_session(session_id)
    print(f"Session sauvegardée dans: {save_path}")
    
    # Charger la session plus tard
    loaded_session_id = dispatcher.load_session(save_path)
    print(f"Session chargée: {loaded_session_id}")
    
    # Afficher l'historique
    history = dispatcher.get_session_history(loaded_session_id)
    print(f"Nombre de messages: {len(history)}")
    
    return dispatcher


if __name__ == "__main__":
    demo_claude_dispatcher()
