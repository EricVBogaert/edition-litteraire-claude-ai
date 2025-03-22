#!/usr/bin/env python
"""
Exemples d'utilisation du gestionnaire de conversation pour UnifiedLLM.
"""

from unified_llm import UnifiedLLM, ModelConfig, Tool
from conversation_manager import ConversationManager


def main():
    """Exemples d'utilisation du gestionnaire de conversation."""
    
    # Initialisation du client UnifiedLLM (détection automatique du fournisseur)
    llm = UnifiedLLM()
    print(f"Fournisseur actif: {llm.get_provider()}")
    
    # Création du gestionnaire de conversation
    manager = ConversationManager(llm)
    
    # Création d'une configuration par défaut
    if llm.get_provider() == "claude":
        model_name = "claude-3-haiku-20240307"
    else:  # lmstudio
        model_name = "qwen2.5-7b-instruct-1m"
    
    config = ModelConfig(
        model_name=model_name,
        temperature=0.7,
        max_tokens=2000
    )
    
    # Exemple 1: Conversation basique avec maintien du contexte
    print("\n\n" + "="*50)
    print("EXEMPLE 1: CONVERSATION BASIQUE AVEC MAINTIEN DU CONTEXTE")
    print("="*50 + "\n")
    
    # Création d'une conversation avec message système
    conversation = manager.create_conversation(
        model_config=config,
        system_message="Tu es un assistant spécialisé dans l'explication de concepts scientifiques."
    )
    
    # Premier message
    print("Utilisateur: Explique-moi ce qu'est la relativité restreinte.")
    response = manager.send_message(
        conversation.id,
        "Explique-moi ce qu'est la relativité restreinte."
    )
    print(f"\nAssistant: {response}\n")
    
    # Deuxième message (avec contexte maintenu)
    print("Utilisateur: Quel est son rapport avec E=mc²?")
    response = manager.send_message(
        conversation.id,
        "Quel est son rapport avec E=mc²?"
    )
    print(f"\nAssistant: {response}\n")
    
    # Troisième message (avec contexte maintenu)
    print("Utilisateur: Et qui a développé cette théorie?")
    response = manager.send_message(
        conversation.id,
        "Et qui a développé cette théorie?"
    )
    print(f"\nAssistant: {response}\n")
    
    
    # Exemple 2: Utilisation des outils
    print("\n\n" + "="*50)
    print("EXEMPLE 2: UTILISATION DES OUTILS AVEC CONVERSATION")
    print("="*50 + "\n")
    
    # Définition d'un outil de calculatrice
    calculator_tool = Tool(
        name="calculatrice",
        description="Effectue des calculs mathématiques",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "L'expression mathématique à évaluer"
                }
            },
            "required": ["expression"]
        }
    )
    
    # Création d'une conversation pour les calculs
    calcul_conversation = manager.create_conversation(
        model_config=config,
        system_message="Tu es un assistant capable d'effectuer des calculs mathématiques."
    )
    
    # Premier message avec outil
    print("Utilisateur: Quel est le résultat de 1234 * 5678?")
    
    # Simulation d'un mode de détection automatique des appels d'outils
    response = manager.send_message(
        calcul_conversation.id,
        "Quel est le résultat de 1234 * 5678?",
        tools=[calculator_tool]  # Met l'outil à disposition
    )
    
    print(f"\nAssistant: {response}\n")
    
    # Simulation de l'exécution de l'outil (dans un vrai scénario, on analyserait la réponse 
    # pour détecter si elle contient un appel d'outil, mais ici on simule directement)
    print("Exécution de l'outil calculatrice...")
    
    # Exécution de l'outil et ajout du résultat à la conversation
    expression = "1234 * 5678"
    result = str(eval(expression))
    
    manager.execute_tool(
        calcul_conversation.id,
        "calculatrice",
        {"expression": expression},
        result
    )
    
    # Demande au modèle de continuer avec le résultat de l'outil
    print("\nAssistant continue avec le résultat de l'outil...")
    response = manager.send_message(
        calcul_conversation.id,
        "Peux-tu vérifier ce calcul et me donner le résultat?"
    )
    print(f"\nAssistant: {response}\n")
    
    
    # Exemple 3: Réinitialisation de conversation
    print("\n\n" + "="*50)
    print("EXEMPLE 3: RÉINITIALISATION DE CONVERSATION")
    print("="*50 + "\n")
    
    # Affichage de l'historique avant réinitialisation
    print("Historique de la conversation de relativité (avant réinitialisation):")
    for i, msg in enumerate(conversation.get_messages()):
        role = "Système" if msg.role.value == "system" else (
               "Utilisateur" if msg.role.value == "user" else "Assistant")
        content = msg.content[:100] + "..." if msg.content and len(msg.content) > 100 else msg.content
        print(f"{i+1}. {role}: {content}")
    
    # Réinitialisation de la conversation (en gardant le message système)
    print("\nRéinitialisation de la conversation...")
    manager.clear_conversation(conversation.id, keep_system=True)
    
    # Affichage de l'historique après réinitialisation
    print("\nHistorique après réinitialisation:")
    for i, msg in enumerate(conversation.get_messages()):
        role = "Système" if msg.role.value == "system" else (
               "Utilisateur" if msg.role.value == "user" else "Assistant")
        print(f"{i+1}. {role}: {msg.content}")
    
    # Nouvelle conversation après réinitialisation
    print("\nNouvelle conversation après réinitialisation:")
    print("Utilisateur: Qu'est-ce que la photosynthèse?")
    response = manager.send_message(
        conversation.id,
        "Qu'est-ce que la photosynthèse?"
    )
    print(f"\nAssistant: {response}\n")
    
    # Exemple 4: Streaming de réponses
    print("\n\n" + "="*50)
    print("EXEMPLE 4: STREAMING DE RÉPONSES")
    print("="*50 + "\n")
    
    # Création d'une conversation pour le streaming
    stream_conversation = manager.create_conversation(model_config=config)
    
    print("Utilisateur: Explique-moi les principes de base du machine learning.")
    print("\nAssistant (streaming): ", end="", flush=True)
    
    try:
        # Envoi du message avec streaming
        for chunk in manager.send_message(
            stream_conversation.id,
            "Explique-moi les principes de base du machine learning.",
            stream=True
        ):
            print(chunk, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"\nErreur lors du streaming: {e}")
    
    # Suppression des conversations
    print("\nSuppression des conversations...")
    manager.delete_conversation(conversation.id)
    manager.delete_conversation(calcul_conversation.id)
    manager.delete_conversation(stream_conversation.id)
    print("Conversations supprimées.")


if __name__ == "__main__":
    main()
