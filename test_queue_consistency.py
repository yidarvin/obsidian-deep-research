#!/usr/bin/env python3
"""
Test script to verify queue-filename consistency
"""

import re
from pathlib import Path

def sanitize_filename(topic):
    """Convert topic to a safe filename that matches wiki links exactly"""
    # Only remove truly problematic characters for filesystems
    # Keep spaces, underscores, and most special characters as they appear in wiki links
    safe_name = re.sub(r'[<>:"/\\|?*]', '', topic)
    safe_name = safe_name[:100]  # Limit length
    return safe_name + '.md'

def test_queue_consistency():
    """Test that queue entries match future filenames exactly"""
    
    # Read the queue file
    queue_path = Path("queue.txt")
    if not queue_path.exists():
        print("Queue file not found")
        return
    
    with open(queue_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"Testing {len(lines)} queue entries...")
    print()
    
    all_match = True
    for i, concept in enumerate(lines, 1):
        if concept:
            # This is what the filename will be (without .md extension)
            future_filename = sanitize_filename(concept).replace('.md', '')
            matches = concept == future_filename
            
            print(f"{i:2d}. Concept: '{concept}'")
            print(f"    Future filename: '{future_filename}'")
            print(f"    Match: {'✓' if matches else '✗'}")
            print()
            
            if not matches:
                all_match = False
    
    if all_match:
        print("✅ All queue entries will match their future filenames exactly!")
    else:
        print("❌ Some queue entries will NOT match their future filenames!")
    
    return all_match

if __name__ == "__main__":
    test_queue_consistency()
