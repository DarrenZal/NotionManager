#!/usr/bin/env python3
"""
Setup script to help configure environment variables for Notion API.
"""

import os

def setup_environment():
    """
    Interactive setup for Notion API credentials.
    """
    print("🔧 Notion API Setup")
    print("=" * 40)
    
    # Get current values if they exist
    current_token = os.getenv('NOTION_TOKEN', '')
    current_db_id = os.getenv('DATABASE_ID', '')
    current_people_db_id = os.getenv('PEOPLE_DATABASE_ID', '')
    current_openai_key = os.getenv('OPENAI_API_KEY', '')
    
    print(f"Current NOTION_TOKEN: {'*' * 20 if current_token else 'Not set'}")
    print(f"Current DATABASE_ID: {current_db_id if current_db_id else 'Not set'}")
    print(f"Current PEOPLE_DATABASE_ID: {current_people_db_id if current_people_db_id else 'Not set'}")
    print(f"Current OPENAI_API_KEY: {'*' * 20 if current_openai_key else 'Not set'}")
    print()
    
    # Get new token
    token_input = input("Enter your Notion integration token (starts with 'secret_'): ").strip()
    if not token_input:
        if current_token:
            token_input = current_token
            print("Using existing token")
        else:
            print("❌ Token is required!")
            return False
    
    # Get new database ID
    db_id_input = input("Enter your Meetings database ID: ").strip()
    if not db_id_input:
        if current_db_id:
            db_id_input = current_db_id
            print("Using existing database ID")
        else:
            print("❌ Database ID is required!")
            return False
    
    # Get People database ID (optional)
    people_db_input = input("Enter your People database ID (optional, for auto-linking): ").strip()
    if not people_db_input:
        if current_people_db_id:
            people_db_input = current_people_db_id
            print("Using existing People database ID")
        else:
            print("ℹ️  People database ID not provided - auto-linking will be disabled")
    
    # Generate export commands
    print("\n" + "=" * 50)
    print("📋 Environment Setup Commands")
    print("=" * 50)
    print("Copy and paste these commands in your terminal:")
    print()
    print(f"export NOTION_TOKEN='{token_input}'")
    print(f"export DATABASE_ID='{db_id_input}'")
    if people_db_input:
        print(f"export PEOPLE_DATABASE_ID='{people_db_input}'")
    print()
    print("Or add them to your ~/.zshrc or ~/.bashrc for persistence:")
    print(f"echo 'export NOTION_TOKEN=\"{token_input}\"' >> ~/.zshrc")
    print(f"echo 'export DATABASE_ID=\"{db_id_input}\"' >> ~/.zshrc")
    if people_db_input:
        print(f"echo 'export PEOPLE_DATABASE_ID=\"{people_db_input}\"' >> ~/.zshrc")
    print()
    print("Then run: source ~/.zshrc")
    
    return True

def create_env_file():
    """
    Create a .env file for local development.
    """
    print("🔧 Creating .env file for easy configuration")
    print("=" * 45)
    
    token = input("Enter your Notion integration token: ").strip()
    db_id = input("Enter your Meetings database ID: ").strip()
    people_db_id = input("Enter your People database ID (optional): ").strip()
    openai_key = input("Enter your OpenAI API key (optional, for transcript processing): ").strip()
    
    if token and db_id:
        with open('.env', 'w') as f:
            f.write(f"# Notion API Configuration\n")
            f.write(f"NOTION_TOKEN={token}\n")
            f.write(f"DATABASE_ID={db_id}\n")
            if people_db_id:
                f.write(f"PEOPLE_DATABASE_ID={people_db_id}\n")
            else:
                f.write(f"# PEOPLE_DATABASE_ID=your_people_database_id_here\n")
            f.write(f"\n# OpenAI API Configuration\n")
            if openai_key:
                f.write(f"OPENAI_API_KEY={openai_key}\n")
            else:
                f.write(f"# OPENAI_API_KEY=sk-your_openai_api_key_here\n")
        
        print("✅ Created .env file")
        print("Note: Make sure to add .env to your .gitignore file!")
        
        # Create .gitignore if it doesn't exist
        if not os.path.exists('.gitignore'):
            with open('.gitignore', 'w') as f:
                f.write(".env\n")
                f.write("__pycache__/\n")
                f.write("*.pyc\n")
                f.write("notion-env/\n")
            print("✅ Created .gitignore file")
        
        return True
    else:
        print("❌ Both token and database ID are required!")
        return False

def main():
    """
    Main setup function.
    """
    print("Choose setup method:")
    print("1. Environment variables (recommended)")
    print("2. .env file (for local development)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        setup_environment()
    elif choice == "2":
        create_env_file()
    else:
        print("Invalid choice. Please run again and select 1 or 2.")

if __name__ == "__main__":
    main()
