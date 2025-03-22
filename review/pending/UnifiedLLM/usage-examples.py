#!/usr/bin/env python
"""
Example usage of UnifiedLLM library.
"""

from unified_llm import UnifiedLLM, ModelConfig, Tool

# Example 1: Basic chat with auto provider selection
def basic_chat_example():
    """Basic chat example with automatic provider selection."""
    # Initialize with auto provider (will prefer LMStudio if available)
    llm = UnifiedLLM()
    
    # Create a config - will use the default model for the active provider
    config = ModelConfig(
        model_name="claude-3-sonnet-20240229" if llm.get_provider() == "claude" else "qwen2.5-7b-instruct-1m",
        temperature=0.7,
        max_tokens=1000
    )
    
    # Create messages
    messages = [
        llm.create_message("user", "Explain quantum computing in simple terms.")
    ]
    
    # Get response
    response = llm.chat(messages, config)
    print(f"Using provider: {llm.get_provider()}")
    print("Response:", response)
    print("\n" + "="*50 + "\n")


# Example 2: Streaming responses with Claude
def streaming_example():
    """Example using streaming responses with Claude."""
    # Try to initialize with Claude (will fail gracefully if not available)
    try:
        llm = UnifiedLLM(provider="claude")
        
        # Create a config
        config = ModelConfig(
            model_name="claude-3-haiku-20240307",
            temperature=0.7,
            max_tokens=1000
        )
        
        # Create messages
        messages = [
            llm.create_message("system", "You are a helpful assistant that responds with short, concise answers."),
            llm.create_message("user", "Write a step-by-step guide to make sourdough bread.")
        ]
        
        # Get streaming response
        print("Streaming response:")
        for chunk in llm.chat(messages, config, stream=True):
            print(chunk, end="", flush=True)
        print("\n\n" + "="*50 + "\n")
    except (ValueError, ImportError) as e:
        print(f"Claude example skipped: {e}")


# Example 3: Tool use with LMStudio
def tool_use_example():
    """Example using tools with LMStudio."""
    try:
        # Initialize with LMStudio
        llm = UnifiedLLM(provider="lmstudio")
        
        # Create a config
        config = ModelConfig(
            model_name="qwen2.5-7b-instruct-1m",  # A model that supports tool calling
            temperature=0.2,  # Lower temperature for more deterministic responses
            max_tokens=1000
        )
        
        # Define a calculator tool
        calculator_tool = llm.create_tool(
            name="calculator",
            description="Perform mathematical calculations",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        )
        
        # Define the calculator function
        def calculator(expression):
            try:
                return str(eval(expression))
            except Exception as e:
                return f"Error: {str(e)}"
        
        # Create messages
        messages = [
            llm.create_message("user", "What is 1345 * 2242?")
        ]
        
        # Get response
        response = llm.chat(messages, config, tools=[calculator_tool])
        
        # Check if the response includes a tool call
        # This part is simplified and would need to be adapted based on 
        # how LMStudio returns tool calls in its responses
        print(f"Using provider: {llm.get_provider()}")
        
        # In a real implementation, we would parse the tool call from the response,
        # execute it, and then send the result back in a follow-up message
        if "calculator" in response and "expression" in response:
            # This is a mock parse of a tool call - implementation would differ
            expression = "1345 * 2242"  # Would extract this from response
            result = calculator(expression)
            
            # Add the tool result to the conversation
            messages.append(llm.create_message(
                "assistant", 
                tool_call={
                    "id": "call_123",
                    "type": "function",
                    "name": "calculator",
                    "arguments": {"expression": expression}
                }
            ))
            
            messages.append(llm.create_message(
                "tool", 
                tool_result={
                    "tool_call_id": "call_123",
                    "content": result
                }
            ))
            
            # Get the final response
            final_response = llm.chat(messages, config)
            print("Final response:", final_response)
        else:
            print("Response:", response)
        
        print("\n" + "="*50 + "\n")
    except (ValueError, ImportError) as e:
        print(f"LMStudio example skipped: {e}")


# Example 4: Embeddings
def embeddings_example():
    """Example generating embeddings with either provider."""
    llm = UnifiedLLM()  # Auto provider
    
    text = "This is a sample text to embed."
    
    embeddings = llm.embed(text)
    print(f"Using provider: {llm.get_provider()}")
    print(f"Generated embedding with {len(embeddings)} dimensions")
    print("First 5 values:", embeddings[:5])
    print("\n" + "="*50 + "\n")


# Example 5: Switching providers
def provider_switching_example():
    """Example showing how to switch between providers."""
    try:
        # Start with auto provider
        llm = UnifiedLLM()
        initial_provider = llm.get_provider()
        print(f"Initial provider: {initial_provider}")
        
        # Get available providers
        available = llm.available_providers()
        print(f"Available providers: {available}")
        
        # Switch to another provider if possible
        if len(available) > 1:
            # Switch to the other provider
            other_provider = [p for p in available if p != initial_provider][0]
            llm.set_provider(other_provider)
            print(f"Switched to: {llm.get_provider()}")
            
            # Get supported models for new provider
            models = llm.supported_models()
            print(f"Supported models by {other_provider}: {models[:3]}...")
        else:
            print(f"Only one provider available: {initial_provider}")
        
        print("\n" + "="*50 + "\n")
    except Exception as e:
        print(f"Provider switching example error: {e}")


if __name__ == "__main__":
    print("\nUNIFIED LLM EXAMPLES\n")
    print("="*50 + "\n")
    
    # Run examples
    basic_chat_example()
    streaming_example()
    tool_use_example()
    embeddings_example()
    provider_switching_example()
