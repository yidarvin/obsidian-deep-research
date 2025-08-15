#!/usr/bin/env python3
"""
Test script to verify the deep research tool setup
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_setup():
    """Test all components of the setup"""
    print("Testing Deep Research Tool Setup...")
    print("=" * 40)
    
    # Test 1: Environment variables
    print("1. Testing environment variables...")
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("   ❌ OPENAI_API_KEY not found in .env file")
        return False
    elif api_key == "your_openai_api_key_here":
        print("   ⚠️  OPENAI_API_KEY is still set to placeholder value")
        return False
    else:
        print("   ✅ OPENAI_API_KEY found")
    
    path_to_save = os.getenv('PATH_TO_SAVE')
    if not path_to_save:
        print("   ❌ PATH_TO_SAVE not found in .env file")
        return False
    elif path_to_save == "/path/to/your/obsidian/vault":
        print("   ⚠️  PATH_TO_SAVE is still set to placeholder value")
        return False
    else:
        print("   ✅ PATH_TO_SAVE found")
    
    # Test 2: Required files
    print("\n2. Testing required files...")
    
    template_path = Path("Simple_Note_Template.md")
    if not template_path.exists():
        print("   ❌ Simple_Note_Template.md not found")
        return False
    else:
        print("   ✅ Simple_Note_Template.md found")
    
    # Test 3: Python packages
    print("\n3. Testing Python packages...")
    
    try:
        import openai
        print("   ✅ openai package installed")
    except ImportError:
        print("   ❌ openai package not installed")
        return False
    
    try:
        import dotenv
        print("   ✅ python-dotenv package installed")
    except ImportError:
        print("   ❌ python-dotenv package not installed")
        return False
    
    # Test 4: Directory access
    print("\n4. Testing directory access...")
    
    try:
        save_path = Path(path_to_save)
        if not save_path.exists():
            print(f"   ⚠️  PATH_TO_SAVE directory does not exist: {path_to_save}")
            print("   Creating directory...")
            save_path.mkdir(parents=True, exist_ok=True)
            print("   ✅ Directory created")
        else:
            print("   ✅ PATH_TO_SAVE directory accessible")
    except Exception as e:
        print(f"   ❌ Cannot access PATH_TO_SAVE: {e}")
        return False
    
    # Test 5: Queue file
    print("\n5. Testing queue file...")
    
    queue_path = Path("queue.txt")
    if not queue_path.exists():
        print("   ⚠️  queue.txt not found, creating...")
        queue_path.touch()
        print("   ✅ queue.txt created")
    else:
        print("   ✅ queue.txt found")
    
    print("\n" + "=" * 40)
    print("✅ Setup test completed successfully!")
    print("\nYou can now use the tool:")
    print("  python deep_research.py \"Your Topic\"")
    print("  python pop_queue.py")
    
    return True

if __name__ == "__main__":
    success = test_setup()
    if not success:
        sys.exit(1)
