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

# Initialize LLM with OpenAI for reduced local processing
llm_backend = "openai"
llm_model = config.get('model', 'gpt-3.5-turbo')
api_key = config.get('OPENAI_API_KEY')

if not api_key or api_key == "sk-YOURAPIKEY":
    print("⚠️  WARNING: No valid API key found!")
    print("Please set your OpenAI API key in the config file.")
    print("Edit potato_config.yaml and replace 'sk-YOURAPIKEY' with your actual API key.")
    api_key = input("Enter your OpenAI API key: ").strip()
    if api_key:
        # Update config temporarily
        config['OPENai_API_KEY'] = api_key

print(f"Initializing LLM with model: {llm_model}")
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
            
            # Add user message to history
            messages.append({"role": "user", "content": user_input})
            
            print("🤔 Riko is thinking...")
            
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