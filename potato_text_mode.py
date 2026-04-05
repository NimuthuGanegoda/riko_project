"""
AI Waifu for Potato Systems - Text Only Mode
A lightweight version that works on low-end hardware without audio processing
"""

import os
import json
import yaml
import logging
from pathlib import Path

# Import only essential modules for text processing
from process.llm_funcs.llm_factory import LLMFactory
from server.memory_manager import MemoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(' \n ========= Starting Potato-Optimized AI Waifu ================ \n')

# Load Config - Use potato config if available, otherwise default
config_path = 'potato_config.yaml' if os.path.exists('potato_config.yaml') else 'character_config.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Set backend to CPU for potato systems
config['backend_preference'] = 'cpu_legacy'
logger.info("Using CPU-only backend for potato system compatibility")

# Initialize LLM with configured provider
llm_backend = config.get('llm_provider', 'openai') # Default to openai but can be gemini or ollama
llm_model = config.get('model', 'gpt-3.5-turbo')
api_key = config.get('OPENAI_API_KEY') if llm_backend != 'gemini' else config.get('GEMINI_API_KEY')

if (llm_backend in ["openai", "gemini"]) and (not api_key or api_key in ["sk-YOURAPIKEY", "YOUR_GEMINI_API_KEY"]):
    print(f"⚠️  WARNING: No valid API key found for {llm_backend}!")
    print(f"Please set your {llm_backend.upper()} API key in the config file.")
    api_key = input(f"Enter your {llm_backend.upper()} API key: ").strip()
    if api_key:
        config[f'{llm_backend.upper()}_API_KEY'] = api_key

print(f"Initializing LLM: {llm_backend} with model: {llm_model}")
llm = LLMFactory.create_llm(llm_backend, llm_model, api_key=api_key)

# History Management
HISTORY_FILE = config.get('history_file', 'chat_history_potato.json')
SYSTEM_PROMPT = [{"role": "system", "content": config['presets']['default']['system_prompt']}]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return list(SYSTEM_PROMPT)

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def clear_history():
    """Clear the conversation history"""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        print("Conversation history cleared.")

def main():
    print("\n🤖 AI Waifu (Potato Edition) Started!")
    print("Commands: 'quit' to exit, 'clear' to reset conversation, 'help' for help")
    
    messages = load_history()
    print(f"\n💬 {messages[0]['content'].split('.')[0]}")  # Show character intro
    
    while True:
        try:
            user_input = input("\n>You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Riko: Bye bye, senpai! See you next time!")
                break
            elif user_input.lower() in ['clear', 'reset']:
                clear_history()
                messages = list(SYSTEM_PROMPT)  # Reset to system prompt only
                print("🔄 Conversation history cleared. Starting fresh!")
                continue
            elif user_input.lower() in ['help', 'h']:
                print("\n📝 Available commands:")
                print("  'quit' or 'q' - Exit the program")
                print("  'clear' - Reset conversation history")
                print("  'help' - Show this help message")
                print("  Any other text - Chat with Riko!")
                continue
            
            # Retrieve long-term memory context
            past_context = memory_db.get_context(user_input, n_results=3)
            if past_context:
                context_msg = f"Relevant past memories:\n{past_context}\n\nUser's current message: {user_input}"
                messages.append({"role": "user", "content": context_msg})
            else:
                messages.append({"role": "user", "content": user_input})
            
            print("🤔 Riko is thinking...")
            
            # Screen Awareness: Read Clipboard
            try:
                clip_text = pyperclip.paste()
                if clip_text and clip_text.strip():
                    messages.append({"role": "system", "content": f"[System: The user's current clipboard contains: '{clip_text[:500]}']"})
            except Exception:
                pass
            
            # Get response from LLM
            try:
                response = llm.generate(messages)
                print(f"💗 Riko: {response}")
                
                # Add assistant response to history
                messages.append({"role": "assistant", "content": response})
                save_history(messages)
                
            except Exception as e:
                print(f"❌ Error getting response: {e}")
                # Remove the user message since we couldn't get a response
                messages.pop()
                continue
                
        except KeyboardInterrupt:
            print("\n\n👋 Riko: See you later, senpai!")
            break
        except EOFError:
            print("\n👋 Riko: See you later, senpai!")
            break

if __name__ == "__main__":
    main()