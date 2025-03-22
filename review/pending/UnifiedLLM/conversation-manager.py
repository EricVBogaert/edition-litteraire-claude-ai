#!/usr/bin/env python
"""
ConversationManager - Extension pour UnifiedLLM permettant la gestion du contexte de conversation.
"""

import uuid
from typing import Dict, List, Optional, Union, Any, Iterator

from unified_llm import UnifiedLLM, Message, ModelConfig, Tool, MessageRole


class Conversation:
    """
    Classe représentant une conversation avec un LLM.
    Gère le maintien du contexte entre les appels.
    """
    
    def __init__(self, model_config: ModelConfig = None, system_message: str = None):
        """
        Initialise une nouvelle conversation.
        
        Args:
            model_config: Configuration du modèle à utiliser pour cette conversation
            system_message: Message système optionnel à utiliser pour cette conversation
        """
        self.id = str(uuid.uuid4())
        self.messages: List[Message] = []
        self.model_config = model_config
        
        # Ajout optionnel d'un message système
        if system_message:
            self.add_system_message(system_message)
    
    def add_system_message(self, content: str) -> None:
        """Ajoute un message système à la conversation."""
        # Vérifie si un message système existe déjà
        for i, msg in enumerate(self.messages):
            if msg.role == MessageRole.SYSTEM:
                # Remplace le message système existant
                self.messages[i] = Message(
                    role=MessageRole.SYSTEM,
                    content=content
                )
                return
        
        # Ajoute un nouveau message système
        self.messages.insert(0, Message(
            role=MessageRole.SYSTEM,
            content=content
        ))
    
    def add_user_message(self, content: str, file_paths: List[str] = None) -> None:
        """Ajoute un message utilisateur à la conversation."""
        self.messages.append(Message(
            role=MessageRole.USER,
            content=content,
            file_paths=file_paths or []
        ))
    
    def add_assistant_message(self, content: str) -> None:
        """Ajoute un message assistant à la conversation."""
        self.messages.append(Message(
            role=MessageRole.ASSISTANT,
            content=content
        ))
    
    def add_tool_call(self, name: str, arguments: Dict[str, Any], id: str = None) -> str:
        """
        Ajoute un appel d'outil à la conversation.
        
        Returns:
            L'ID de l'appel d'outil
        """
        tool_call_id = id or f"call_{uuid.uuid4().hex[:8]}"
        
        self.messages.append(Message(
            role=MessageRole.ASSISTANT,
            tool_call={
                "id": tool_call_id,
                "type": "function",
                "name": name,
                "arguments": arguments
            }
        ))
        
        return tool_call_id
    
    def add_tool_result(self, tool_call_id: str, content: str) -> None:
        """Ajoute un résultat d'outil à la conversation."""
        self.messages.append(Message(
            role=MessageRole.TOOL,
            tool_result={
                "tool_call_id": tool_call_id,
                "content": content
            }
        ))
    
    def get_messages(self) -> List[Message]:
        """Retourne les messages de la conversation."""
        return self.messages
    
    def clear_messages(self, keep_system: bool = True) -> None:
        """
        Efface les messages de la conversation.
        
        Args:
            keep_system: Si True, conserve le message système
        """
        if keep_system:
            system_messages = [msg for msg in self.messages if msg.role == MessageRole.SYSTEM]
            self.messages = system_messages
        else:
            self.messages = []


class ConversationManager:
    """
    Gestionnaire de conversations pour UnifiedLLM.
    Permet de maintenir le contexte entre les appels de façon transparente.
    """
    
    def __init__(self, llm: UnifiedLLM):
        """
        Initialise le gestionnaire de conversations.
        
        Args:
            llm: Instance UnifiedLLM à utiliser
        """
        self.llm = llm
        self.conversations: Dict[str, Conversation] = {}
        
        # Stockage des objets Chat LMStudio pour réutilisation
        self._lmstudio_chats = {}
    
    def create_conversation(self, model_config: ModelConfig = None, 
                           system_message: str = None) -> Conversation:
        """
        Crée une nouvelle conversation.
        
        Returns:
            La nouvelle conversation créée
        """
        conversation = Conversation(model_config, system_message)
        self.conversations[conversation.id] = conversation
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Récupère une conversation par son ID."""
        return self.conversations.get(conversation_id)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Supprime une conversation.
        
        Returns:
            True si la conversation a été supprimée, False sinon
        """
        if conversation_id in self.conversations:
            # Nettoie aussi le chat LMStudio associé si nécessaire
            if conversation_id in self._lmstudio_chats:
                del self._lmstudio_chats[conversation_id]
            
            del self.conversations[conversation_id]
            return True
        return False
    
    def _get_or_create_lmstudio_chat(self, conversation_id: str) -> Any:
        """
        Récupère ou crée un objet Chat LMStudio pour une conversation.
        Ce chat persistant permet de maintenir le contexte dans LMStudio.
        """
        if self.llm.get_provider() != "lmstudio":
            return None
            
        if conversation_id not in self._lmstudio_chats:
            # Importe le module lmstudio
            import lmstudio as lms
            
            # Récupère la conversation
            conversation = self.conversations[conversation_id]
            
            # Crée un nouveau chat LMStudio
            chat = lms.Chat()
            
            # Si un message système existe, l'ajouter
            system_messages = [msg for msg in conversation.messages 
                              if msg.role == MessageRole.SYSTEM]
            if system_messages:
                chat.system = system_messages[0].content
            
            self._lmstudio_chats[conversation_id] = chat
            
        return self._lmstudio_chats[conversation_id]
    
    def send_message(self, conversation_id: str, message: str, 
                     file_paths: List[str] = None,
                     model_config: ModelConfig = None, 
                     tools: List[Tool] = None,
                     stream: bool = False) -> Union[str, Iterator[str]]:
        """
        Envoie un message dans une conversation et récupère la réponse.
        
        Args:
            conversation_id: ID de la conversation
            message: Message à envoyer
            file_paths: Chemins des fichiers à joindre
            model_config: Configuration de modèle à utiliser (remplace celle de la conversation)
            tools: Outils à mettre à disposition du modèle
            stream: Si True, retourne un générateur de fragments de réponse
            
        Returns:
            La réponse du modèle ou un générateur de fragments
        """
        # Récupère la conversation
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation inconnue: {conversation_id}")
        
        # Ajoute le message utilisateur
        conversation.add_user_message(message, file_paths)
        
        # Détermine la configuration du modèle à utiliser
        config = model_config or conversation.model_config
        if not config:
            raise ValueError("Aucune configuration de modèle spécifiée")
        
        # Optimisation pour LMStudio: utilise un objet Chat persistant
        if self.llm.get_provider() == "lmstudio":
            try:
                # Récupère le chat LMStudio persistant
                chat = self._get_or_create_lmstudio_chat(conversation_id)
                
                # Ajoute le message utilisateur au chat LMStudio
                chat.add_user_message(message)
                
                # Configure la requête pour LMStudio
                lmstudio_config = {
                    "temperature": config.temperature,
                    "maxTokens": config.max_tokens,
                    "topPSampling": config.top_p,
                    "stopStrings": config.stop_sequences
                }
                
                # Ajoute les outils si fournis
                if tools:
                    lmstudio_tools = []
                    for tool in tools:
                        lmstudio_tools.append(tool.to_dict())
                    
                    lmstudio_config["rawTools"] = {
                        "type": "toolArray",
                        "tools": lmstudio_tools
                    }
                
                # Récupère directement le fournisseur LMStudio
                lmstudio_provider = self.llm.providers["lmstudio"]
                model = lmstudio_provider._get_or_load_model(config.model_name)
                
                if stream:
                    # Stream response fragments
                    prediction_stream = model.respond_stream(
                        chat,
                        config=lmstudio_config,
                        on_message=chat.append,
                    )
                    
                    def response_generator():
                        full_response = ""
                        for fragment in prediction_stream:
                            yield fragment.content
                            full_response += fragment.content
                        
                        # Stocke la réponse complète dans l'historique
                        conversation.add_assistant_message(full_response)
                    
                    return response_generator()
                else:
                    # Get complete response at once
                    response = model.respond(
                        chat,
                        config=lmstudio_config,
                    )
                    
                    # Stocke la réponse dans l'historique
                    conversation.add_assistant_message(response)
                    
                    return response
                
            except Exception as e:
                # En cas d'erreur, on revient à l'approche standard
                print(f"Erreur lors de l'utilisation directe de LMStudio: {e}")
                print("Revenir à la méthode standard...")
        
        # Pour Claude ou en cas d'échec de l'optimisation LMStudio:
        # Utilise l'approche standard en passant tout l'historique
        response = self.llm.chat(conversation.messages, config, tools, stream)
        
        if not stream:
            # Stocke la réponse dans l'historique si pas en mode stream
            conversation.add_assistant_message(response)
        
        return response
    
    def execute_tool(self, conversation_id: str, tool_name: str, 
                     arguments: Dict[str, Any], tool_result: str) -> None:
        """
        Exécute un outil et ajoute le résultat à la conversation.
        
        Args:
            conversation_id: ID de la conversation
            tool_name: Nom de l'outil
            arguments: Arguments de l'outil
            tool_result: Résultat de l'exécution de l'outil
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation inconnue: {conversation_id}")
        
        # Ajoute l'appel d'outil et son résultat
        tool_call_id = conversation.add_tool_call(tool_name, arguments)
        conversation.add_tool_result(tool_call_id, tool_result)
        
        # Si LMStudio, met à jour le chat persistant
        if conversation_id in self._lmstudio_chats:
            try:
                chat = self._lmstudio_chats[conversation_id]
                
                # Ajoute l'appel d'outil
                chat.messages.append({
                    "role": "assistant",
                    "content": [{
                        "type": "toolCallRequest",
                        "toolCallRequest": {
                            "id": tool_call_id,
                            "type": "function",
                            "name": tool_name,
                            "arguments": arguments
                        }
                    }]
                })
                
                # Ajoute le résultat de l'outil
                chat.messages.append({
                    "role": "tool",
                    "content": [{
                        "type": "toolCallResult",
                        "content": tool_result,
                        "toolCallId": tool_call_id
                    }]
                })
            except Exception as e:
                print(f"Erreur lors de la mise à jour du chat LMStudio: {e}")
    
    def clear_conversation(self, conversation_id: str, keep_system: bool = True) -> None:
        """
        Efface les messages d'une conversation.
        
        Args:
            conversation_id: ID de la conversation
            keep_system: Si True, conserve le message système
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation inconnue: {conversation_id}")
        
        # Sauvegarde le message système si demandé
        system_message = None
        if keep_system:
            system_messages = [msg for msg in conversation.messages 
                              if msg.role == MessageRole.SYSTEM]
            if system_messages:
                system_message = system_messages[0].content
        
        # Efface les messages
        conversation.clear_messages(keep_system)
        
        # Réinitialise le chat LMStudio si nécessaire
        if conversation_id in self._lmstudio_chats:
            try:
                import lmstudio as lms
                chat = lms.Chat()
                
                # Restaure le message système si demandé
                if keep_system and system_message:
                    chat.system = system_message
                
                self._lmstudio_chats[conversation_id] = chat
            except Exception as e:
                print(f"Erreur lors de la réinitialisation du chat LMStudio: {e}")
