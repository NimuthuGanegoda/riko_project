#!/usr/bin/env python3
import os
import sys
import argparse

# Add the backend to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    parser = argparse.ArgumentParser(description="🌸 Project Riko: The Autonomous AI Companion")
    parser.add_argument("--web", action="store_true", help="Run the Web API server")
    parser.add_argument("--chat", action="store_true", help="Run the Terminal Chat interface")
    
    args = parser.parse_args()
    
    if args.web:
        print("🚀 Starting Riko Web API...")
        os.system(f"{sys.executable} backend/api.py")
    elif args.chat:
        print("💬 Starting Riko Terminal Chat...")
        os.system(f"{sys.executable} backend/main_chat.py")
    else:
        print("Please specify a mode: --web or --chat")
        parser.print_help()

if __name__ == "__main__":
    main()
