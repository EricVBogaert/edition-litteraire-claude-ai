#!/usr/bin/env python
"""
Gestionnaire de credentials pour UnifiedLLM.
Prend en charge plusieurs fournisseurs et méthodes d'authentification.
"""

import os
import json
import keyring
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from enum import Enum


class CredentialSource(Enum):
    """Sources possibles pour les credentials."""
    ENV = "environment"         # Variables d'environnement
    CONFIG_FILE = "config_file" # Fichier de configuration
    KEYRING = "keyring"         # Stockage sécurisé du système
    EXPLICIT = "explicit"       # Fourni explicitement par l'utilisateur


class CredentialManager:
    """
    Gestionnaire centralisé des credentials pour différents fournisseurs d'IA.
    Prend en charge plusieurs méthodes de stockage et d'accès.
    """
    
    # Définition des configurations par fournisseur
    PROVIDER_CONFIGS = {
        "claude": {
            "env_vars": ["ANTHROPIC_API_KEY"],
            "config_keys": ["anthropic_api_key", "claude_api_key"],
            "keyring_service": "unified_llm_claude",
            "required_keys": ["api_key"],
            "optional_keys": ["api_url", "organization_id"],
        },
        "lmstudio": {
            "env_vars": ["LMSTUDIO_API_KEY"],
            "config_keys": ["lmstudio_api_key"],
            "keyring_service": "unified_llm_lmstudio",
            "required_keys": [],  # LMStudio local n'a pas besoin de clé
            "optional_keys": ["api_url", "api_key"],  # Pour version serveur
        },
        "openai": {  # Préparation pour extension future
            "env_vars": ["OPENAI_API_KEY"],
            "config_keys": ["openai_api_key"],
            "keyring_service": "unified_llm_openai",
            "required_keys": ["api_key"],
            "optional_keys": ["api_url", "organization_id"],
        },
        "gemini": {  # Préparation pour extension future
            "env_vars": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
            "config_keys": ["google_api_key", "gemini_api_key"],
            "keyring_service": "unified_llm_gemini",
            "required_keys": ["api_key"],
            "optional_keys": ["api_url", "project_id"],
        },
        # Ajoutez d'autres fournisseurs selon les besoins
    }
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialise le gestionnaire de credentials.
        
        Args:
            config_path: Chemin vers le fichier de configuration (optionnel)
        """
        self.credentials: Dict[str, Dict[str, Any]] = {}
        self.config_path = Path(config_path) if config_path else Path.home() / ".unified_llm" / "config.json"
        self.sources: Dict[str, Dict[str, CredentialSource]] = {}
        
        # Charger les credentials disponibles
        self._load_all_credentials()
    
    def _load_all_credentials(self) -> None:
        """Charge les credentials de toutes les sources pour tous les fournisseurs."""
        # Crée le répertoire de configuration s'il n'existe pas
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Charge les credentials de chaque fournisseur
        for provider in self.PROVIDER_CONFIGS:
            self._load_provider_credentials(provider)
    
    def _load_provider_credentials(self, provider: str) -> None:
        """
        Charge les credentials pour un fournisseur spécifique.
        
        Args:
            provider: Nom du fournisseur
        """
        if provider not in self.PROVIDER_CONFIGS:
            return
        
        provider_config = self.PROVIDER_CONFIGS[provider]
        self.credentials[provider] = {}
        self.sources[provider] = {}
        
        # 1. Essaie de charger depuis les variables d'environnement
        for env_var in provider_config["env_vars"]:
            if env_var in os.environ:
                self.credentials[provider]["api_key"] = os.environ[env_var]
                self.sources[provider]["api_key"] = CredentialSource.ENV
                break
        
        # 2. Essaie de charger depuis le fichier de configuration
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                
                for config_key in provider_config["config_keys"]:
                    if config_key in config:
                        # Si c'est un dictionnaire, utilise tous ses éléments
                        if isinstance(config[config_key], dict):
                            for k, v in config[config_key].items():
                                self.credentials[provider][k] = v
                                self.sources[provider][k] = CredentialSource.CONFIG_FILE
                        # Sinon, considère que c'est la clé API
                        else:
                            self.credentials[provider]["api_key"] = config[config_key]
                            self.sources[provider]["api_key"] = CredentialSource.CONFIG_FILE
            except (json.JSONDecodeError, IOError):
                # Si le fichier est invalide ou inaccessible, on continue
                pass
        
        # 3. Essaie de charger depuis le gestionnaire de mots de passe du système
        try:
            service = provider_config["keyring_service"]
            api_key = keyring.get_password(service, "api_key")
            if api_key:
                self.credentials[provider]["api_key"] = api_key
                self.sources[provider]["api_key"] = CredentialSource.KEYRING
        except Exception:
            # Si keyring n'est pas disponible ou échoue, on continue
            pass
    
    def save_credentials(self, provider: str, credentials: Dict[str, Any], 
                        source: CredentialSource = CredentialSource.CONFIG_FILE) -> None:
        """
        Enregistre les credentials pour un fournisseur spécifique.
        
        Args:
            provider: Nom du fournisseur
            credentials: Dictionnaire des credentials à enregistrer
            source: Source où enregistrer les credentials
        """
        if provider not in self.PROVIDER_CONFIGS:
            raise ValueError(f"Fournisseur non pris en charge: {provider}")
        
        # Met à jour les credentials en mémoire
        self.credentials.setdefault(provider, {}).update(credentials)
        for key in credentials:
            self.sources.setdefault(provider, {})[key] = source
        
        # Enregistre selon la source spécifiée
        if source == CredentialSource.ENV:
            # Pour les variables d'environnement, on affiche juste un message
            provider_config = self.PROVIDER_CONFIGS[provider]
            if "api_key" in credentials and provider_config["env_vars"]:
                print(f"Pour enregistrer comme variable d'environnement, utilisez: export {provider_config['env_vars'][0]}={credentials['api_key']}")
        
        elif source == CredentialSource.CONFIG_FILE:
            # Charge la configuration existante ou crée une nouvelle
            config = {}
            if self.config_path.exists():
                try:
                    with open(self.config_path, "r") as f:
                        config = json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass
            
            # Met à jour la configuration
            provider_config = self.PROVIDER_CONFIGS[provider]
            if provider_config["config_keys"]:
                config_key = provider_config["config_keys"][0]
                config[config_key] = credentials
            
            # Enregistre la configuration
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
        
        elif source == CredentialSource.KEYRING:
            # Enregistre les credentials dans le gestionnaire de mots de passe
            try:
                service = self.PROVIDER_CONFIGS[provider]["keyring_service"]
                for key, value in credentials.items():
                    keyring.set_password(service, key, value)
            except Exception as e:
                raise ValueError(f"Impossible d'enregistrer les credentials dans le keyring: {e}")
    
    def get_credentials(self, provider: str) -> Dict[str, Any]:
        """
        Récupère les credentials pour un fournisseur spécifique.
        
        Args:
            provider: Nom du fournisseur
            
        Returns:
            Dictionnaire des credentials disponibles
        """
        return self.credentials.get(provider, {})
    
    def set_api_key(self, provider: str, api_key: str, 
                   source: CredentialSource = CredentialSource.CONFIG_FILE) -> None:
        """
        Définit la clé API pour un fournisseur spécifique.
        
        Args:
            provider: Nom du fournisseur
            api_key: Clé API à définir
            source: Source où enregistrer la clé API
        """
        self.save_credentials(provider, {"api_key": api_key}, source)
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Récupère la clé API pour un fournisseur spécifique.
        
        Args:
            provider: Nom du fournisseur
            
        Returns:
            Clé API ou None si non disponible
        """
        return self.credentials.get(provider, {}).get("api_key")
    
    def credential_source(self, provider: str, credential_key: str = "api_key") -> Optional[CredentialSource]:
        """
        Récupère la source d'un credential spécifique.
        
        Args:
            provider: Nom du fournisseur
            credential_key: Clé du credential
            
        Returns:
            Source du credential ou None si non disponible
        """
        return self.sources.get(provider, {}).get(credential_key)
    
    def check_provider_credentials(self, provider: str) -> Dict[str, bool]:
        """
        Vérifie si tous les credentials nécessaires sont disponibles pour un fournisseur.
        
        Args:
            provider: Nom du fournisseur
            
        Returns:
            Dictionnaire avec les clés requises et leur disponibilité
        """
        if provider not in self.PROVIDER_CONFIGS:
            raise ValueError(f"Fournisseur non pris en charge: {provider}")
        
        result = {}
        provider_config = self.PROVIDER_CONFIGS[provider]
        provider_creds = self.credentials.get(provider, {})
        
        # Vérifie les clés requises
        for key in provider_config["required_keys"]:
            result[key] = key in provider_creds
        
        # Vérifie les clés optionnelles
        for key in provider_config["optional_keys"]:
            if key not in result:  # Ne pas écraser les clés requises
                result[key] = key in provider_creds
        
        return result
    
    def is_provider_configured(self, provider: str) -> bool:
        """
        Vérifie si un fournisseur est correctement configuré.
        
        Args:
            provider: Nom du fournisseur
            
        Returns:
            True si le fournisseur est correctement configuré, False sinon
        """
        if provider not in self.PROVIDER_CONFIGS:
            return False
        
        provider_config = self.PROVIDER_CONFIGS[provider]
        provider_creds = self.credentials.get(provider, {})
        
        # Vérifie que toutes les clés requises sont présentes
        for key in provider_config["required_keys"]:
            if key not in provider_creds:
                return False
        
        return True
    
    def get_configured_providers(self) -> List[str]:
        """
        Récupère la liste des fournisseurs correctement configurés.
        
        Returns:
            Liste des noms de fournisseurs configurés
        """
        return [provider for provider in self.PROVIDER_CONFIGS 
                if self.is_provider_configured(provider)]
    
    def clear_credentials(self, provider: str, source: Optional[CredentialSource] = None) -> None:
        """
        Supprime les credentials d'un fournisseur.
        
        Args:
            provider: Nom du fournisseur
            source: Source spécifique à effacer, ou toutes si None
        """
        if provider not in self.PROVIDER_CONFIGS:
            return
        
        # Si une source spécifique est demandée, supprime uniquement de cette source
        if source:
            if source == CredentialSource.CONFIG_FILE:
                if self.config_path.exists():
                    try:
                        with open(self.config_path, "r") as f:
                            config = json.load(f)
                        
                        provider_config = self.PROVIDER_CONFIGS[provider]
                        for config_key in provider_config["config_keys"]:
                            if config_key in config:
                                del config[config_key]
                        
                        with open(self.config_path, "w") as f:
                            json.dump(config, f, indent=2)
                    except (json.JSONDecodeError, IOError):
                        pass
            
            elif source == CredentialSource.KEYRING:
                try:
                    service = self.PROVIDER_CONFIGS[provider]["keyring_service"]
                    for key in list(self.credentials.get(provider, {}).keys()):
                        try:
                            keyring.delete_password(service, key)
                        except Exception:
                            pass
                except Exception:
                    pass
            
            # Ne peut pas supprimer des variables d'environnement
            
            # Supprime de la mémoire uniquement les credentials de cette source
            if provider in self.sources:
                keys_to_remove = [k for k, src in self.sources[provider].items() if src == source]
                for key in keys_to_remove:
                    if key in self.credentials.get(provider, {}):
                        del self.credentials[provider][key]
                    if key in self.sources[provider]:
                        del self.sources[provider][key]
        
        # Sinon, supprime toutes les credentials (sauf env)
        else:
            # Supprime du fichier de configuration
            self.clear_credentials(provider, CredentialSource.CONFIG_FILE)
            # Supprime du keyring
            self.clear_credentials(provider, CredentialSource.KEYRING)
            
            # Supprime de la mémoire (sauf celles des variables d'environnement)
            if provider in self.sources:
                keys_to_remove = [k for k, src in self.sources[provider].items() 
                                 if src != CredentialSource.ENV]
                for key in keys_to_remove:
                    if key in self.credentials.get(provider, {}):
                        del self.credentials[provider][key]
                    if key in self.sources[provider]:
                        del self.sources[provider][key]
        
        # Recharge les credentials disponibles (pour garder les variables d'environnement)
        self._load_provider_credentials(provider)
