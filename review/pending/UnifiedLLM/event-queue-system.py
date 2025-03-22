#!/usr/bin/env python
"""
Système de file d'événements pour UnifiedLLM.
Implémente une architecture basée sur les événements façon Windows 3.11.
"""

import asyncio
import uuid
import time
import logging
import json
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Callable, Awaitable, Union, Set
from datetime import datetime
import threading
import queue
from contextlib import contextmanager


class EventType(Enum):
    """Types d'événements supportés par le système."""
    SYSTEM_INIT = auto()
    SYSTEM_SHUTDOWN = auto()
    
    CONFIG_CHANGE = auto()
    
    PROVIDER_INIT = auto()
    PROVIDER_CHANGE = auto()
    
    CREDENTIAL_ADDED = auto()
    CREDENTIAL_REMOVED = auto()
    CREDENTIAL_UPDATED = auto()
    
    MODEL_LOADED = auto()
    MODEL_UNLOADED = auto()
    
    CHAT_REQUEST = auto()
    CHAT_RESPONSE = auto()
    CHAT_FRAGMENT = auto()
    CHAT_COMPLETE = auto()
    CHAT_ERROR = auto()
    
    EMBED_REQUEST = auto()
    EMBED_RESPONSE = auto()
    EMBED_ERROR = auto()
    
    CONVERSATION_CREATED = auto()
    CONVERSATION_UPDATED = auto()
    CONVERSATION_DELETED = auto()
    
    TOOL_CALL = auto()
    TOOL_RESULT = auto()
    
    LOG_INFO = auto()
    LOG_WARNING = auto()
    LOG_ERROR = auto()
    LOG_DEBUG = auto()
    
    CUSTOM = auto()  # Pour les extensions


@dataclass
class Event:
    """Représentation d'un événement dans le système."""
    type: EventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    handled: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'événement en dictionnaire."""
        result = asdict(self)
        result["type"] = self.type.name
        return result
    
    def to_json(self) -> str:
        """Convertit l'événement en JSON."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Crée un événement à partir d'un dictionnaire."""
        # Convertir le nom du type en énumération
        event_type = EventType[data.pop("type")]
        return cls(type=event_type, **data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Event':
        """Crée un événement à partir d'une chaîne JSON."""
        return cls.from_dict(json.loads(json_str))


class EventQueue:
    """
    File d'attente d'événements centrale.
    Supporte les modes synchrone et asynchrone.
    """
    
    def __init__(self, enable_logging: bool = True, 
                log_level: int = logging.INFO,
                log_file: Optional[str] = None,
                remote_logging: Optional[Dict[str, Any]] = None):
        """
        Initialise la file d'événements.
        
        Args:
            enable_logging: Si True, active la journalisation des événements
            log_level: Niveau de journalisation
            log_file: Fichier de journalisation, si None, utilise stderr
            remote_logging: Configuration pour la journalisation distante (syslog)
        """
        # File d'attente synchrone
        self._sync_queue = queue.Queue()
        
        # File d'attente asynchrone
        self._async_queue = asyncio.Queue()
        
        # Thread de traitement pour le mode synchrone
        self._processing_thread = None
        self._stop_event = threading.Event()
        
        # Gestionnaires d'événements
        self._sync_handlers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._async_handlers: Dict[EventType, List[Callable[[Event], Awaitable[None]]]] = {}
        self._subscribers: Dict[str, Set[EventType]] = {}
        
        # Configuration de la journalisation
        self.enable_logging = enable_logging
        if enable_logging:
            self._setup_logging(log_level, log_file)
            
            # Configuration de syslog si demandé
            if remote_logging:
                self._setup_remote_logging(remote_logging)
    
    def _setup_logging(self, log_level: int, log_file: Optional[str]) -> None:
        """Configure la journalisation locale."""
        self.logger = logging.getLogger("event_queue")
        self.logger.setLevel(log_level)
        
        # Formateur
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Gestionnaire
        if log_file:
            handler = logging.FileHandler(log_file)
        else:
            handler = logging.StreamHandler()
        
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _setup_remote_logging(self, config: Dict[str, Any]) -> None:
        """Configure la journalisation distante (syslog)."""
        try:
            import logging.handlers
            
            # Configuration par défaut
            host = config.get("host", "localhost")
            port = config.get("port", 514)
            facility = config.get("facility", logging.handlers.SysLogHandler.LOG_USER)
            
            # Créer le gestionnaire syslog
            syslog_handler = logging.handlers.SysLogHandler(
                address=(host, port),
                facility=facility
            )
            
            # Formateur spécifique à syslog
            formatter = logging.Formatter('UnifiedLLM: %(message)s')
            syslog_handler.setFormatter(formatter)
            
            # Ajouter au logger
            self.logger.addHandler(syslog_handler)
            self.logger.info(f"Remote logging enabled to {host}:{port}")
            
        except ImportError:
            self.logger.error("Could not import logging.handlers for remote logging")
        except Exception as e:
            self.logger.error(f"Failed to set up remote logging: {e}")
    
    def start(self) -> None:
        """Démarre le traitement des événements dans un thread séparé."""
        if self._processing_thread is not None and self._processing_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._processing_thread = threading.Thread(
            target=self._process_events_loop,
            daemon=True,
            name="EventQueueProcessor"
        )
        self._processing_thread.start()
        
        # Émettre un événement d'initialisation
        self.emit(Event(
            type=EventType.SYSTEM_INIT,
            source="event_queue",
            data={"timestamp": datetime.now().isoformat()}
        ))
    
    def stop(self) -> None:
        """Arrête le traitement des événements."""
        if self._processing_thread is None or not self._processing_thread.is_alive():
            return
        
        # Émettre un événement d'arrêt
        self.emit(Event(
            type=EventType.SYSTEM_SHUTDOWN,
            source="event_queue",
            data={"timestamp": datetime.now().isoformat()}
        ))
        
        # Attendre un peu pour traiter l'événement d'arrêt
        time.sleep(0.1)
        
        # Arrêter le thread
        self._stop_event.set()
        self._processing_thread.join(timeout=2.0)
        
        if self._processing_thread.is_alive():
            self.logger.warning("Event processing thread did not stop gracefully")
    
    def _process_events_loop(self) -> None:
        """Boucle principale de traitement des événements (synchrone)."""
        while not self._stop_event.is_set():
            try:
                # Attendre un événement avec timeout pour pouvoir vérifier self._stop_event
                try:
                    event = self._sync_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Journaliser l'événement
                if self.enable_logging:
                    self._log_event(event)
                
                # Copier dans la file asynchrone si des gestionnaires asynchrones sont enregistrés
                if event.type in self._async_handlers:
                    asyncio.run_coroutine_threadsafe(
                        self._async_queue.put(event),
                        asyncio.get_event_loop()
                    )
                
                # Traiter l'événement avec les gestionnaires synchrones
                self._process_sync_event(event)
                
                # Marquer comme terminé
                self._sync_queue.task_done()
                
            except Exception as e:
                if self.enable_logging:
                    self.logger.error(f"Error processing event: {e}")
    
    def _process_sync_event(self, event: Event) -> None:
        """
        Traite un événement avec les gestionnaires synchrones.
        
        Args:
            event: Événement à traiter
        """
        # Trouver les gestionnaires pour ce type d'événement
        handlers = self._sync_handlers.get(event.type, [])
        
        # Si aucun gestionnaire, marquer comme non traité
        if not handlers:
            if self.enable_logging:
                self.logger.debug(f"No handlers for event {event.type.name}")
            return
        
        # Appeler les gestionnaires
        for handler in handlers:
            try:
                handler(event)
                event.handled = True
            except Exception as e:
                if self.enable_logging:
                    self.logger.error(f"Error in sync handler for {event.type.name}: {e}")
    
    async def _process_async_event(self, event: Event) -> None:
        """
        Traite un événement avec les gestionnaires asynchrones.
        
        Args:
            event: Événement à traiter
        """
        # Trouver les gestionnaires pour ce type d'événement
        handlers = self._async_handlers.get(event.type, [])
        
        # Si aucun gestionnaire, marquer comme non traité
        if not handlers:
            if self.enable_logging:
                self.logger.debug(f"No async handlers for event {event.type.name}")
            return
        
        # Appeler les gestionnaires
        for handler in handlers:
            try:
                await handler(event)
                event.handled = True
            except Exception as e:
                if self.enable_logging:
                    self.logger.error(f"Error in async handler for {event.type.name}: {e}")
    
    async def process_events_async(self) -> None:
        """
        Boucle de traitement asynchrone des événements.
        À utiliser dans une application asynchrone comme FastAPI.
        """
        while True:
            event = await self._async_queue.get()
            
            # Journaliser l'événement
            if self.enable_logging:
                self._log_event(event)
            
            # Traiter l'événement
            await self._process_async_event(event)
            
            # Marquer comme terminé
            self._async_queue.task_done()
    
    def _log_event(self, event: Event) -> None:
        """Journalise un événement."""
        # Déterminer le niveau de journalisation en fonction du type d'événement
        if event.type in (EventType.LOG_ERROR, EventType.CHAT_ERROR, EventType.EMBED_ERROR):
            log_level = logging.ERROR
        elif event.type == EventType.LOG_WARNING:
            log_level = logging.WARNING
        elif event.type == EventType.LOG_DEBUG:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        
        # Journaliser
        self.logger.log(
            log_level,
            f"Event {event.id}: {event.type.name} from {event.source} - {json.dumps(event.data)}"
        )
    
    def emit(self, event: Event) -> None:
        """
        Émet un événement dans la file d'attente synchrone.
        
        Args:
            event: Événement à émettre
        """
        self._sync_queue.put(event)
    
    async def emit_async(self, event: Event) -> None:
        """
        Émet un événement dans la file d'attente asynchrone.
        
        Args:
            event: Événement à émettre
        """
        await self._async_queue.put(event)
        
        # Assurer que l'événement est également dans la file synchrone
        self._sync_queue.put(event)
    
    def register_handler(self, event_type: EventType, 
                        handler: Callable[[Event], None],
                        subscriber_id: str = None) -> None:
        """
        Enregistre un gestionnaire d'événements synchrone.
        
        Args:
            event_type: Type d'événement à gérer
            handler: Fonction à appeler pour traiter l'événement
            subscriber_id: Identifiant de l'abonné (pour le suivi)
        """
        if event_type not in self._sync_handlers:
            self._sync_handlers[event_type] = []
        
        self._sync_handlers[event_type].append(handler)
        
        # Suivre l'abonnement
        if subscriber_id:
            if subscriber_id not in self._subscribers:
                self._subscribers[subscriber_id] = set()
            self._subscribers[subscriber_id].add(event_type)
    
    def register_async_handler(self, event_type: EventType, 
                              handler: Callable[[Event], Awaitable[None]],
                              subscriber_id: str = None) -> None:
        """
        Enregistre un gestionnaire d'événements asynchrone.
        
        Args:
            event_type: Type d'événement à gérer
            handler: Coroutine à appeler pour traiter l'événement
            subscriber_id: Identifiant de l'abonné (pour le suivi)
        """
        if event_type not in self._async_handlers:
            self._async_handlers[event_type] = []
        
        self._async_handlers[event_type].append(handler)
        
        # Suivre l'abonnement
        if subscriber_id:
            if subscriber_id not in self._subscribers:
                self._subscribers[subscriber_id] = set()
            self._subscribers[subscriber_id].add(event_type)
    
    def unregister_handler(self, event_type: EventType, 
                          handler: Callable[[Event], None]) -> None:
        """
        Désenregistre un gestionnaire d'événements synchrone.
        
        Args:
            event_type: Type d'événement
            handler: Fonction à désenregistrer
        """
        if event_type in self._sync_handlers:
            self._sync_handlers[event_type] = [
                h for h in self._sync_handlers[event_type] if h != handler
            ]
    
    def unregister_async_handler(self, event_type: EventType, 
                               handler: Callable[[Event], Awaitable[None]]) -> None:
        """
        Désenregistre un gestionnaire d'événements asynchrone.
        
        Args:
            event_type: Type d'événement
            handler: Coroutine à désenregistrer
        """
        if event_type in self._async_handlers:
            self._async_handlers[event_type] = [
                h for h in self._async_handlers[event_type] if h != handler
            ]
    
    def unregister_subscriber(self, subscriber_id: str) -> None:
        """
        Désenregistre tous les gestionnaires d'un abonné.
        
        Args:
            subscriber_id: Identifiant de l'abonné
        """
        if subscriber_id not in self._subscribers:
            return
        
        # Récupérer les types d'événements souscrits
        event_types = self._subscribers[subscriber_id]
        
        # Supprimer de _subscribers
        del self._subscribers[subscriber_id]
        
        # TODO: Implémenter la suppression des gestionnaires par abonné
        # Cette fonctionnalité nécessite de stocker l'association entre
        # subscriber_id et handlers spécifiques
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Récupère des statistiques sur la file d'attente.
        
        Returns:
            Statistiques de la file
        """
        return {
            "sync_queue_size": self._sync_queue.qsize(),
            "async_queue_size": self._async_queue.qsize(),
            "registered_event_types": {
                "sync": list(self._sync_handlers.keys()),
                "async": list(self._async_handlers.keys())
            },
            "subscribers_count": len(self._subscribers),
            "subscribers": {
                sub_id: [et.name for et in events] 
                for sub_id, events in self._subscribers.items()
            }
        }


# Singleton pour la file d'événements
_event_queue_instance = None

def get_event_queue() -> EventQueue:
    """
    Récupère l'instance singleton de la file d'événements.
    
    Returns:
        Instance de la file d'événements
    """
    global _event_queue_instance
    if _event_queue_instance is None:
        _event_queue_instance = EventQueue()
        _event_queue_instance.start()
    return _event_queue_instance


@contextmanager
def event_context(source: str):
    """
    Gestionnaire de contexte pour émettre des événements de début et de fin.
    
    Args:
        source: Source des événements
    """
    event_queue = get_event_queue()
    start_time = time.time()
    
    # Émettre un événement de début
    event_queue.emit(Event(
        type=EventType.LOG_DEBUG,
        source=source,
        data={"action": "start", "timestamp": start_time}
    ))
    
    try:
        yield
    except Exception as e:
        # Émettre un événement d'erreur
        event_queue.emit(Event(
            type=EventType.LOG_ERROR,
            source=source,
            data={"error": str(e), "timestamp": time.time()}
        ))
        raise
    finally:
        # Émettre un événement de fin
        end_time = time.time()
        event_queue.emit(Event(
            type=EventType.LOG_DEBUG,
            source=source,
            data={
                "action": "end", 
                "timestamp": end_time,
                "duration": end_time - start_time
            }
        ))
