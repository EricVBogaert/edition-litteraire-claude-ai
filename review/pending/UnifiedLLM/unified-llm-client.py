#!/usr/bin/env python
"""
UnifiedLLM - A transparent abstraction layer over multiple LLM APIs.
Currently supports Claude API and LMStudio.
"""

import os
import json
import base64
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Callable, Iterator, TypedDict

# Optional dependencies
try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import lmstudio as lms
except ImportError:
    lms = None


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ToolCall(TypedDict):
    id: str
    type: str
    name: str
    arguments: Dict[str, Any]


class ToolCallResult(TypedDict):
    tool_call_id: str
    content: str


class Message:
    def __init__(self, role: MessageRole, content: str = None, file_paths: List[str] = None, 
                 tool_call: Optional[ToolCall] = None, tool_result: Optional[ToolCallResult] = None):
        self.role = role
        self.content = content
        self.file_paths = file_paths or []
        self.tool_call = tool_call
        self.tool_result = tool_result
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"role": self.role.value}
        
        if self.content:
            result["content"] = self.content
            
        if self.file_paths:
            # Implementation depends on provider-specific handling
            result["file_paths"] = self.file_paths
            
        if self.tool_call:
            result["tool_call"] = self.tool_call
            
        if self.tool_result:
            result["tool_result"] = self.tool_result
            
        return result


class Tool:
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class ModelConfig:
    def __init__(
        self, 
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        top_p: float = 0.9,
        stop_sequences: List[str] = None,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stop_sequences = stop_sequences or []


class LLMProvider(ABC):
    """Abstract base class defining the interface for LLM providers."""
    
    @abstractmethod
    def chat(self, messages: List[Message], config: ModelConfig, 
             tools: List[Tool] = None, stream: bool = False) -> Union[str, Iterator[str]]:
        """Sends a conversation to the LLM and returns the response."""
        pass
    
    @abstractmethod
    def embed(self, text: str, model_name: str = None) -> List[float]:
        """Generates an embedding for the provided text."""
        pass
    
    @abstractmethod
    def supported_models(self) -> List[str]:
        """Returns a list of models supported by this provider."""
        pass


class ClaudeProvider(LLMProvider):
    """Claude API implementation"""
    
    def __init__(self, api_key: str = None):
        if anthropic is None:
            raise ImportError("anthropic package is required for ClaudeProvider")
        
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Claude API key is required")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert our Message objects to Claude API format."""
        claude_messages = []
        
        for message in messages:
            content = []
            
            # Handle text content
            if message.content:
                content.append({"type": "text", "text": message.content})
            
            # Handle files
            for file_path in message.file_paths:
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    mime_type = self._guess_mime_type(file_path)
                    content.append({
                        "type": "image" if mime_type.startswith("image/") else "file",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": base64.b64encode(file_content).decode()
                        }
                    })
            
            # Handle tool results
            if message.tool_result:
                claude_messages.append({
                    "role": "assistant",
                    "content": [{"type": "tool_call", "id": message.tool_result["tool_call_id"]}]
                })
                claude_messages.append({
                    "role": "tool",
                    "content": message.tool_result["content"],
                    "tool_call_id": message.tool_result["tool_call_id"]
                })
                continue
            
            claude_messages.append({
                "role": message.role.value,
                "content": content
            })
        
        return claude_messages
    
    def _guess_mime_type(self, file_path: str) -> str:
        """Simple mime type detection based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.json': 'application/json',
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def chat(self, messages: List[Message], config: ModelConfig, 
             tools: List[Tool] = None, stream: bool = False) -> Union[str, Iterator[str]]:
        """Send chat messages to Claude and return the response."""
        claude_messages = self._convert_messages(messages)
        
        claude_tools = None
        if tools:
            claude_tools = [tool.to_dict() for tool in tools]
        
        if stream:
            response = self.client.messages.create(
                model=config.model_name,
                messages=claude_messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                stop_sequences=config.stop_sequences,
                tools=claude_tools,
                stream=True
            )
            
            def response_generator():
                for chunk in response:
                    if chunk.type == "content_block_delta" and chunk.delta.type == "text":
                        yield chunk.delta.text
            
            return response_generator()
        else:
            response = self.client.messages.create(
                model=config.model_name,
                messages=claude_messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                stop_sequences=config.stop_sequences,
                tools=claude_tools,
            )
            
            # Extract text content from response
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text
            
            return content
    
    def embed(self, text: str, model_name: str = None) -> List[float]:
        """Generate embeddings using Claude API."""
        model = model_name or "claude-3-sonnet-20240229"
        response = self.client.embeddings.create(
            input=text,
            model=model
        )
        return response.embedding
    
    def supported_models(self) -> List[str]:
        """Return the list of Claude models supported."""
        return [
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229", 
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2"
        ]


class LMStudioProvider(LLMProvider):
    """LMStudio implementation"""
    
    def __init__(self):
        if lms is None:
            raise ImportError("lmstudio package is required for LMStudioProvider")
        
        # Initialize LMStudio clients
        self._loaded_models = {}
    
    def _get_or_load_model(self, model_name: str):
        """Get an already loaded model or load it if needed."""
        if model_name not in self._loaded_models:
            # LMStudio allows loading models by name/identifier
            self._loaded_models[model_name] = lms.llm(model_name)
        return self._loaded_models[model_name]
    
    def _convert_messages(self, messages: List[Message]) -> lms.Chat:
        """Convert our Message objects to LMStudio Chat format."""
        # Initialize an empty chat
        chat = lms.Chat()
        
        for message in messages:
            if message.role == MessageRole.SYSTEM:
                # Set system message in the chat
                chat.system = message.content
            
            elif message.role == MessageRole.USER:
                # Add user message
                content = []
                
                # Add text content
                if message.content:
                    content.append({
                        "type": "text",
                        "text": message.content
                    })
                
                # Add file content if any
                for file_path in message.file_paths:
                    content.append({
                        "type": "file",
                        "name": os.path.basename(file_path),
                        "identifier": file_path
                    })
                
                # Add message to chat
                if len(content) == 1 and "text" in content[0]:
                    # Simple text message
                    chat.add_user_message(content[0]["text"])
                else:
                    # Complex message with multiple parts
                    chat.messages.append({
                        "role": "user",
                        "content": content
                    })
            
            elif message.role == MessageRole.ASSISTANT:
                if message.content:
                    chat.add_assistant_message(message.content)
                elif message.tool_call:
                    # Add tool call part to the chat
                    tool_call_content = [{
                        "type": "toolCallRequest",
                        "toolCallRequest": message.tool_call
                    }]
                    chat.messages.append({
                        "role": "assistant",
                        "content": tool_call_content
                    })
            
            elif message.role == MessageRole.TOOL:
                # Add tool result
                if message.tool_result:
                    chat.messages.append({
                        "role": "tool",
                        "content": [{
                            "type": "toolCallResult",
                            "content": message.tool_result["content"],
                            "toolCallId": message.tool_result.get("tool_call_id", "")
                        }]
                    })
        
        return chat
    
    def _convert_tools(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """Convert our Tool objects to LMStudio format."""
        return [tool.to_dict() for tool in tools]
    
    def chat(self, messages: List[Message], config: ModelConfig, 
             tools: List[Tool] = None, stream: bool = False) -> Union[str, Iterator[str]]:
        """Send chat messages to LMStudio and return the response."""
        model = self._get_or_load_model(config.model_name)
        chat = self._convert_messages(messages)
        
        # Prepare config for LMStudio
        lmstudio_config = {
            "temperature": config.temperature,
            "maxTokens": config.max_tokens,
            "topPSampling": config.top_p,
            "stopStrings": config.stop_sequences
        }
        
        # Add tools if provided
        if tools:
            lmstudio_tools = self._convert_tools(tools)
            lmstudio_config["rawTools"] = {
                "type": "toolArray",
                "tools": lmstudio_tools
            }
        
        if stream:
            # Stream response fragments
            prediction_stream = model.respond_stream(
                chat,
                config=lmstudio_config,
                on_message=chat.append,
            )
            
            def response_generator():
                for fragment in prediction_stream:
                    yield fragment.content
            
            return response_generator()
        else:
            # Get complete response at once
            response = model.respond(
                chat,
                config=lmstudio_config,
            )
            return response
    
    def embed(self, text: str, model_name: str = None) -> List[float]:
        """Generate embeddings using LMStudio."""
        if model_name is None:
            # Find a suitable embedding model
            loaded_models = lms.embedding.rpc.list_loaded()
            if loaded_models:
                embedding_model = loaded_models[0]
            else:
                # Try to load a default embedding model
                embedding_model = lms.embedding.channel.get_or_load("embedding-model")
        else:
            embedding_model = lms.embedding.channel.get_or_load(model_name)
        
        # Generate embeddings
        result = lms.embedding.rpc.embed_string(
            modelSpecifier={"type": "instanceReference", "instanceReference": embedding_model.instance_reference},
            inputString=text
        )
        return result.embedding
    
    def supported_models(self) -> List[str]:
        """Return the list of models available in LMStudio."""
        # This would ideally get the list of available models from LMStudio
        try:
            models = lms.system.rpc.list_downloaded_models()
            return [model.model_key for model in models]
        except:
            # Fallback to returning some common model names
            return ["qwen2.5-7b-instruct-1m", "gemma-7b-instruct", "llama3-8b-instruct", "mistral-7b-instruct"]


class UnifiedLLM:
    """Unified interface for multiple LLM providers."""
    
    def __init__(self, provider: str = "auto", api_key: str = None):
        """
        Initialize the UnifiedLLM client.
        
        Args:
            provider: The LLM provider to use ('claude', 'lmstudio', or 'auto')
            api_key: API key for cloud providers (Claude)
        """
        self.providers = {}
        
        # Try to initialize available providers
        if provider in ["claude", "auto"] and anthropic is not None:
            try:
                self.providers["claude"] = ClaudeProvider(api_key)
            except (ImportError, ValueError) as e:
                if provider == "claude":
                    raise e
        
        if provider in ["lmstudio", "auto"] and lms is not None:
            try:
                self.providers["lmstudio"] = LMStudioProvider()
            except ImportError as e:
                if provider == "lmstudio":
                    raise e
        
        if not self.providers:
            available = []
            if anthropic is not None:
                available.append("claude")
            if lms is not None:
                available.append("lmstudio")
            
            if available:
                raise ValueError(f"Could not initialize any of the requested providers. Available: {available}")
            else:
                raise ImportError("No LLM provider packages are installed. Please install 'anthropic' or 'lmstudio'.")
        
        # Select the active provider
        if provider == "auto":
            # Prefer LMStudio for local inference
            self.active_provider = "lmstudio" if "lmstudio" in self.providers else "claude"
        else:
            self.active_provider = provider
    
    def set_provider(self, provider: str):
        """Change the active provider."""
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' is not available. Available providers: {list(self.providers.keys())}")
        self.active_provider = provider
    
    def get_provider(self) -> str:
        """Get the name of the currently active provider."""
        return self.active_provider
    
    def available_providers(self) -> List[str]:
        """Get the list of available providers."""
        return list(self.providers.keys())
    
    def chat(self, messages: List[Message], config: ModelConfig, 
             tools: List[Tool] = None, stream: bool = False) -> Union[str, Iterator[str]]:
        """Send a conversation to the active LLM provider."""
        provider = self.providers[self.active_provider]
        return provider.chat(messages, config, tools, stream)
    
    def embed(self, text: str, model_name: str = None) -> List[float]:
        """Generate embeddings using the active provider."""
        provider = self.providers[self.active_provider]
        return provider.embed(text, model_name)
    
    def supported_models(self) -> List[str]:
        """Get the list of models supported by the active provider."""
        provider = self.providers[self.active_provider]
        return provider.supported_models()
    
    def create_message(self, role: str, content: str = None, file_paths: List[str] = None,
                      tool_call: Dict[str, Any] = None, tool_result: Dict[str, Any] = None) -> Message:
        """Helper to create a properly formatted message."""
        return Message(
            role=MessageRole(role), 
            content=content, 
            file_paths=file_paths, 
            tool_call=tool_call, 
            tool_result=tool_result
        )
    
    def create_tool(self, name: str, description: str, parameters: Dict[str, Any]) -> Tool:
        """Helper to create a properly formatted tool definition."""
        return Tool(name, description, parameters)
