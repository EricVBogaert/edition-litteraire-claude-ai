#!/usr/bin/env python
"""
Intégration du gestionnaire de credentials avec UnifiedLLM.
Démonstration de l'architecture complète avec interface double (sync/async).
"""

import asyncio
import os
from typing import Dict, List, Optional, Union, Any, Callable, Iterator, TypedDict, Awaitable
from enum import Enum

# Import des modules de la bibliothèque
from unified_llm import Message, ModelConfig, Tool, MessageRole
from conversation_manager import Conversation, ConversationManager
from credential_manager import CredentialManager, CredentialSource


class UnifiedLLMAsync:
    """
    Version avec support asynchrone complet du client UnifiedLLM.
    Cette classe offre les deux interfaces : synchrone et asynchrone.
    Elle intègre également la gestion des credentials et des conversations.
    """
    
    def __init__(self, provider: str = "auto", 
                api_key: str = None,
                config_path: str = None):
        """
        Initialise le client UnifiedLLM avec support asynchrone.
        
        Args:
            provider: Le fournisseur à utiliser ('claude', 'lmstudio', 'auto')
            api_key: Clé API explicite (optionnelle)
            config_path: Chemin vers un fichier de configuration personnalisé
        """
        # Initialise le gestionnaire de credentials
        self.credentials = CredentialManager(config_path)
        
        # Si une clé API est fournie explicitement, l'enregistrer
        if api_key and provider != "auto":
            self.credentials.set_api_key(
                provider, 
                api_key, 
                CredentialSource.EXPLICIT
            )
        
        # Détermine les fournisseurs disponibles
        self.available_providers = self._init_available_providers()
        
        # Sélectionne le fournisseur actif
        self.active_provider = self._select_provider(provider)
        
        # Initialise le gestionnaire de conversations
        self.conversations = ConversationManager(self)
    
    def _init_available_providers(self) -> Dict[str, Any]:
        """
        Initialise les clients pour tous les fournisseurs disponibles.
        
        Returns:
            Dictionnaire des fournisseurs disponibles
        """
        providers = {}
        
        # Tente d'initialiser Claude
        if self._can_initialize_claude():
            try:
                from claude_provider import ClaudeProvider
                api_key = self.credentials.get_api_key("claude")
                providers["claude"] = ClaudeProvider(api_key)
            except (ImportError, Exception) as e:
                print(f"Avertissement: Impossible d'initialiser Claude - {e}")
        
        # Tente d'initialiser LMStudio
        if self._can_initialize_lmstudio():
            try:
                from lmstudio_provider import LMStudioProvider
                creds = self.credentials.get_credentials("lmstudio")
                providers["lmstudio"] = LMStudioProvider(
                    api_url=creds.get("api_url", None),
                    api_key=creds.get("api_key", None)
                )
            except (ImportError, Exception) as e:
                print(f"Avertissement: Impossible d'initialiser LMStudio - {e}")
        
        # Autres fournisseurs à ajouter ici...
        
        return providers
    
    def _can_initialize_claude(self) -> bool:
        """Vérifie si Claude peut être initialisé."""
        try:
            import anthropic
            return self.credentials.is_provider_configured("claude")
        except ImportError:
            return False
    
    def _can_initialize_lmstudio(self) -> bool:
        """Vérifie si LMStudio peut être initialisé."""
        try:
            import lmstudio
            # LMStudio local n'a pas besoin de credentials
            return True
        except ImportError:
            return False
    
    def _select_provider(self, requested_provider: str) -> str:
        """
        Sélectionne le fournisseur actif en fonction de la disponibilité.
        
        Args:
            requested_provider: Fournisseur demandé par l'utilisateur
            
        Returns:
            Nom du fournisseur sélectionné
        
        Raises:
            ValueError: Si aucun fournisseur n'est disponible
        """
        if not self.available_providers:
            raise ValueError(
                "Aucun fournisseur disponible. Installez 'anthropic' ou 'lmstudio' "
                "et configurez les clés API nécessaires."
            )
        
        if requested_provider == "auto":
            # Préfère LMStudio pour l'inférence locale
            if "lmstudio" in self.available_providers:
                return "lmstudio"
            # Sinon, prend le premier disponible
            return next(iter(self.available_providers.keys()))
        
        elif requested_provider in self.available_providers:
            return requested_provider
        
        else:
            available = list(self.available_providers.keys())
            raise ValueError(
                f"Fournisseur '{requested_provider}' non disponible. "
                f"Fournisseurs disponibles: {available}"
            )
    
    #
    # Interface publique - Gestion des fournisseurs
    #
    
    def get_provider(self) -> str:
        """Récupère le nom du fournisseur actif."""
        return self.active_provider
    
    def set_provider(self, provider: str) -> None:
        """
        Change le fournisseur actif.
        
        Args:
            provider: Nom du fournisseur à utiliser
            
        Raises:
            ValueError: Si le fournisseur n'est pas disponible
        """
        self.active_provider = self._select_provider(provider)
    
    def list_providers(self) -> List[str]:
        """
        Liste les fournisseurs disponibles.
        
        Returns:
            Liste des noms de fournisseurs disponibles
        """
        return list(self.available_providers.keys())
    
    #
    # Interface publique - Gestion des credentials
    #
    
    def set_api_key(self, provider: str, api_key: str) -> None:
        """
        Définit la clé API pour un fournisseur.
        
        Args:
            provider: Nom du fournisseur
            api_key: Clé API à définir
        """
        self.credentials.set_api_key(provider, api_key)
        
        # Réinitialise les fournisseurs pour prendre en compte la nouvelle clé
        self.available_providers = self._init_available_providers()
    
    def configure_provider(self, provider: str, config: Dict[str, Any]) -> None:
        """
        Configure un fournisseur avec des paramètres personnalisés.
        
        Args:
            provider: Nom du fournisseur
            config: Configuration du fournisseur (api_key, api_url, etc.)
        """
        self.credentials.save_credentials(provider, config)
        
        # Réinitialise les fournisseurs pour prendre en compte la nouvelle configuration
        self.available_providers = self._init_available_providers()
    
    #
    # Interface publique - Fonctions LLM synchrones
    #
    
    def chat(self, messages: List[Message], config: ModelConfig, 
             tools: List[Tool] = None, stream: bool = False) -> Union[str, Iterator[str]]:
        """
        Version synchrone de chat.
        Envoie des messages à un LLM et récupère la réponse.
        
        Args:
            messages: Liste des messages à envoyer
            config: Configuration du modèle
            tools: Liste des outils à mettre à disposition
            stream: Si True, retourne un générateur de fragments
            
        Returns:
            Réponse du modèle ou générateur de fragments
        """
        return self._run_sync(self.chat_async(messages, config, tools, stream))
    
    def embed(self, text: str, model_name: str = None) -> List[float]:
        """
        Version synchrone de embed.
        Génère un embedding pour un texte.
        
        Args:
            text: Texte à encoder
            model_name: Nom du modèle à utiliser (optionnel)
            
        Returns:
            Vecteur d'embedding
        """
        return self._run_sync(self.embed_async(text, model_name))
    
    def supported_models(self) -> List[str]:
        """
        Version synchrone de supported_models.
        Liste les modèles supportés par le fournisseur actif.
        
        Returns:
            Liste des noms de modèles supportés
        """
        return self._run_sync(self.supported_models_async())
    
    #
    # Interface publique - Fonctions LLM asynchrones
    #
    
    async def chat_async(self, messages: List[Message], config: ModelConfig, 
                        tools: List[Tool] = None, stream: bool = False) -> Union[str, Iterator[str]]:
        """
        Version asynchrone de chat.
        Envoie des messages à un LLM et récupère la réponse.
        
        Args:
            messages: Liste des messages à envoyer
            config: Configuration du modèle
            tools: Liste des outils à mettre à disposition
            stream: Si True, retourne un générateur de fragments
            
        Returns:
            Réponse du modèle ou générateur de fragments
        """
        provider = self.available_providers[self.active_provider]
        return await provider.chat_async(messages, config, tools, stream)
    
    async def embed_async(self, text: str, model_name: str = None) -> List[float]:
        """
        Version asynchrone de embed.
        Génère un embedding pour un texte.
        
        Args:
            text: Texte à encoder
            model_name: Nom du modèle à utiliser (optionnel)
            
        Returns:
            Vecteur d'embedding
        """
        provider = self.available_providers[self.active_provider]
        return await provider.embed_async(text, model_name)
    
    async def supported_models_async(self) -> List[str]:
        """
        Version asynchrone de supported_models.
        Liste les modèles supportés par le fournisseur actif.
        
        Returns:
            Liste des noms de modèles supportés
        """
        provider = self.available_providers[self.active_provider]
        return await provider.supported_models_async()
    
    #
    # Utilitaires
    #
    
    def _run_sync(self, coroutine: Awaitable):
        """
        Exécute une coroutine de manière synchrone.
        
        Args:
            coroutine: Coroutine à exécuter
            
        Returns:
            Résultat de la coroutine
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Dans un environnement async existant, créer un nouveau loop
                return asyncio.run_coroutine_threadsafe(coroutine, loop).result()
            else:
                # Pas de loop en cours, utiliser asyncio.run
                return asyncio.run(coroutine)
        except RuntimeError:
            # Si pas de loop d'événement, en créer un
            return asyncio.run(coroutine)
    
    #
    # Helpers pour la création d'objets
    #
    
    def create_message(self, role: str, content: str = None, file_paths: List[str] = None,
                      tool_call: Dict[str, Any] = None, tool_result: Dict[str, Any] = None) -> Message:
        """
        Crée un message formaté correctement.
        
        Args:
            role: Rôle du message ('system', 'user', 'assistant', 'tool')
            content: Contenu du message
            file_paths: Chemins des fichiers joints
            tool_call: Appel d'outil (pour messages assistant)
            tool_result: Résultat d'outil (pour messages tool)
            
        Returns:
            Message formaté
        """
        return Message(
            role=MessageRole(role),
            content=content,
            file_paths=file_paths or [],
            tool_call=tool_call,
            tool_result=tool_result
        )
    
    def create_tool(self, name: str, description: str, parameters: Dict[str, Any]) -> Tool:
        """
        Crée une définition d'outil formatée correctement.
        
        Args:
            name: Nom de l'outil
            description: Description de l'outil
            parameters: Paramètres de l'outil (schéma JSON)
            
        Returns:
            Définition d'outil
        """
        return Tool(name, description, parameters)
    
    def create_conversation(self, model_config: ModelConfig = None, 
                           system_message: str = None) -> Conversation:
        """
        Crée une nouvelle conversation.
        
        Args:
            model_config: Configuration du modèle
            system_message: Message système initial
            
        Returns:
            Nouvelle conversation
        """
        return self.conversations.create_conversation(model_config, system_message)


# Pour compatibilité avec le code existant - alias par défaut
UnifiedLLM = UnifiedLLMAsync
