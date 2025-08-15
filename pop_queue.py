#!/usr/bin/env python3
"""
Queue Processor for Deep Research
Takes the first concept from queue.txt and processes it with deep_research.py
"""

import os
import sys
import re
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def sanitize_filename(topic):
    """Convert topic to a safe filename that matches wiki links exactly"""
    # Only remove truly problematic characters for filesystems
    # Keep spaces, underscores, and most special characters as they appear in wiki links
    safe_name = re.sub(r'[<>:"/\\|?*]', '', topic)
    safe_name = safe_name[:100]  # Limit length
    return safe_name + '.md'

def topic_exists(topic):
    """Check if a topic already exists in the save directory"""
    path_to_save = os.getenv('PATH_TO_SAVE')
    if not path_to_save:
        print("Warning: PATH_TO_SAVE not set in .env file")
        return False
    
    filename = sanitize_filename(topic)
    filepath = Path(path_to_save) / filename
    
    return filepath.exists()

def read_queue():
    """Read the queue file and return all items"""
    queue_path = Path("queue.txt")
    if not queue_path.exists():
        return []
    
    with open(queue_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def write_queue(items):
    """Write items back to the queue file"""
    with open("queue.txt", 'w') as f:
        for item in items:
            f.write(f"{item}\n")

def pop_and_research():
    """Take the first item from queue and research it"""
    queue_items = read_queue()
    
    if not queue_items:
        print("Queue is empty!")
        return False
    
    # Get the first item
    topic = queue_items[0]
    remaining_items = queue_items[1:]
    
    print(f"Processing: {topic}")
    print(f"Remaining in queue: {len(remaining_items)} items")
    
    # Check if topic already exists
    if topic_exists(topic):
        print(f"Topic '{topic}' already exists. Skipping research.")
        # Remove the processed item from queue
        write_queue(remaining_items)
        print(f"Removed '{topic}' from queue")
        return True
    
    # Run the research
    try:
        result = subprocess.run([
            sys.executable, "deep_research.py", topic
        ], capture_output=True, text=True, check=True)
        
        print("Research completed successfully!")
        print(result.stdout)
        
        # Remove the processed item from queue
        write_queue(remaining_items)
        print(f"Removed '{topic}' from queue")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during research: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("Usage: python pop_queue.py [OPTION] [COUNT]")
        print("")
        print("Options:")
        print("  --list, -l          List all items in the queue")
        print("  --clear             Clear the entire queue")
        print("  --check <topic>     Check if a topic already exists")
        print("  --help, -h          Show this help message")
        print("")
        print("Arguments:")
        print("  COUNT               Number of items to process (default: 1)")
        print("")
        print("Examples:")
        print("  python pop_queue.py              # Process 1 item")
        print("  python pop_queue.py 3            # Process 3 items")
        print("  python pop_queue.py --list       # List queue contents")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        # List queue contents
        queue_items = read_queue()
        if queue_items:
            print("Current queue:")
            for i, item in enumerate(queue_items, 1):
                print(f"{i}. {item}")
        else:
            print("Queue is empty!")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        # Clear the queue
        write_queue([])
        print("Queue cleared!")
        return
    
    if len(sys.argv) > 2 and sys.argv[1] == "--check":
        # Check if a specific topic exists
        topic = sys.argv[2]
        if topic_exists(topic):
            print(f"Topic '{topic}' already exists in the save directory.")
        else:
            print(f"Topic '{topic}' does not exist yet.")
        return
    
    # Determine how many items to process
    count = 1  # Default to 1
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
            if count <= 0:
                print("Error: Count must be a positive integer")
                sys.exit(1)
        except ValueError:
            print("Error: Count must be a valid integer")
            sys.exit(1)
    
    # Process the specified number of items
    success_count = 0
    for i in range(count):
        print(f"\n--- Processing item {i + 1} of {count} ---")
        success = pop_and_research()
        if success:
            success_count += 1
        else:
            print(f"Failed to process item {i + 1}. Stopping.")
            break
    
    print(f"\nCompleted: {success_count} of {count} items processed successfully")
    if success_count < count:
        sys.exit(1)

if __name__ == "__main__":
    main()
