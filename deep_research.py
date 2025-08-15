#!/usr/bin/env python3
"""
Deep Research Tool for Obsidian
Uses OpenAI's o4-mini-deep-research model to create comprehensive research notes
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class DeepResearch:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.path_to_save = os.getenv('PATH_TO_SAVE')
        if not self.path_to_save:
            raise ValueError("PATH_TO_SAVE not set in .env file")
        
        # Ensure the directory exists
        Path(self.path_to_save).mkdir(parents=True, exist_ok=True)
        
        # Load the template
        self.template_path = Path("Simple_Note_Template.md")
        if not self.template_path.exists():
            raise FileNotFoundError("Simple_Note_Template.md not found")
        
        with open(self.template_path, 'r') as f:
            self.template = f.read()

    def sanitize_filename(self, topic):
        """Convert topic to a safe filename that matches wiki links exactly"""
        # Only remove truly problematic characters for filesystems
        # Keep spaces, underscores, and most special characters as they appear in wiki links
        safe_name = re.sub(r'[<>:"/\\|?*]', '', topic)
        safe_name = safe_name[:100]  # Limit length
        return safe_name + '.md'

    def _messages_to_responses_input(self, messages):
        """Convert messages to the format expected by the Responses API"""
        structured = []
        for m in messages:
            role = m.get("role", "user")
            content_text = m.get("content", "")
            # Map roles to appropriate content block types for the Responses API
            if role == "assistant":
                block_type = "output_text"
                mapped_role = "assistant"
            else:
                # Treat user/system as user input text
                block_type = "input_text"
                mapped_role = "user" if role != "assistant" else "assistant"
            structured.append({
                "role": mapped_role,
                "content": [
                    {"type": block_type, "text": content_text}
                ],
            })
        return structured

    def research_topic(self, topic):
        """Use OpenAI to research the topic"""
        prompt = f"""
        Research the topic: "{topic}"
        
        IMPORTANT CONSTRAINTS:
        - Keep research SHALLOW and BRIEF to avoid rate limits
        - Focus on 3-5 key points maximum
        - Keep summary under 200 words
        - Prioritize breadth over depth
        - DO NOT manually add wiki links - they will be added automatically
        
        Create a brief research note with:
        1. Short summary (2-3 sentences)
        2. 3-5 key points only
        3. 2-3 related concepts (just list them normally, no wiki links)
        4. 1-2 questions for future research
        
        Keep the response concise and focused on the most essential information only.
        Key concepts will be automatically converted to wiki links during processing.
        """

        try:
            # Format the input for the Responses API
            messages = [{"role": "user", "content": prompt}]
            input_data = self._messages_to_responses_input(messages)
            
            # Use the responses API for o4-mini-deep-research model with web search tools
            response = self.client.responses.create(
                model="o4-mini-deep-research",
                input=input_data,
                tools=[{"type": "web_search_preview"}]
            )
            
            # Handle response with proper fallbacks
            text = getattr(response, "output_text", None)
            if text is None:
                # Fallback: attempt to read from first output
                try:
                    text = response.output[0].content[0].text
                except Exception:
                    text = ""
            
            return text or ""
        except Exception as e:
            print(f"Error during research: {e}")
            return None

    def create_note(self, topic, research_content, existing_links=None):
        """Create the note file with proper frontmatter"""
        filename = self.sanitize_filename(topic)
        filepath = Path(self.path_to_save) / filename
        
        # Create frontmatter
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        frontmatter = f"""---
title: "{topic}"
aliases: []
tags: [research, {topic.lower().replace(' ', '_')}]
created: "{current_time}"
modified: "{current_time}"
note_type: "research"
---

"""
        
        # Add existing links to the content if provided
        if existing_links:
            # Find the Related Notes section and add existing links
            if "## Related Notes" in research_content:
                existing_links_section = "\n### Existing Notes\n"
                for link in existing_links:
                    existing_links_section += f"- [[{link}]]\n"
                research_content = research_content.replace("## Related Notes", existing_links_section + "\n## Related Notes")
        
        # Combine frontmatter with research content
        full_content = frontmatter + research_content
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return filepath

    def find_existing_links(self, new_content):
        """Find existing files that can be linked to the new content"""
        existing_files = []
        for file_path in Path(self.path_to_save).glob("*.md"):
            if file_path.name != "Simple_Note_Template.md":
                # Use the filename stem (without .md) as the topic name
                existing_files.append(file_path.stem)
        
        if not existing_files:
            return []
        
        # Use a cheaper model to find relevant links
        prompt = f"""
        Given this research content:
        
        {new_content[:1000]}...
        
        And these existing note titles:
        {existing_files}
        
        Which existing notes (if any) should be linked to this new content?
        Return only the titles that are directly relevant, separated by commas.
        If none are relevant, return "none".
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that identifies relevant connections between research notes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            if result.lower() == "none":
                return []
            
            return [title.strip() for title in result.split(',')]
        except Exception as e:
            print(f"Error finding links: {e}")
            return []

    def extract_wiki_links(self, content):
        """Extract wiki-links from content that don't exist yet"""
        # Extract wiki links using regex - this gets exactly what's inside [[...]]
        wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
        
        # Clean up the extracted links (remove any whitespace)
        wiki_links = [link.strip() for link in wiki_links if link.strip()]
        
        # Get existing files using the same sanitization logic
        existing_files = set()
        for f in Path(self.path_to_save).glob("*.md"):
            if f.name != "Simple_Note_Template.md":
                # Remove .md extension to get the original topic name
                existing_files.add(f.stem)
        
        # Filter out existing files and return new concepts
        # These will be exact matches to what's inside the wiki links
        new_concepts = [link for link in wiki_links if link not in existing_files]
        
        print(f"DEBUG: Extracted wiki links: {wiki_links}")
        print(f"DEBUG: Existing files: {list(existing_files)[:5]}...")
        print(f"DEBUG: New concepts for queue: {new_concepts}")
        
        return new_concepts

    def identify_and_link_key_concepts(self, content, topic):
        """Identify key concepts in the content and convert them to wiki links"""
        print(f"DEBUG: Starting key concept identification for topic: {topic}")
        print(f"DEBUG: Content length: {len(content)} characters")
        
        # Get existing files to avoid linking to concepts that already exist
        existing_files = set()
        for f in Path(self.path_to_save).glob("*.md"):
            if f.name != "Simple_Note_Template.md":
                existing_files.add(f.stem)
        
        print(f"DEBUG: Found {len(existing_files)} existing files: {list(existing_files)[:5]}...")
        
        # Use AI to identify key concepts that should be wiki-linked
        prompt = f"""
        Analyze this research content and identify key concepts that should be wiki-linked.
        
        Research Topic: {topic}
        
        Content:
        {content}
        
        Instructions:
        1. Identify important concepts, terms, people, places, theories, or ideas that could have their own research page
        2. Focus on concepts that are significant enough to warrant their own note
        3. Exclude the main topic itself and very common/generic terms
        4. Return only the concept names, one per line
        5. Use the exact spelling/capitalization as they appear in the text
        
        Example concepts that should be linked:
        - Specific theories (e.g., "Quantum Mechanics", "Evolutionary Theory")
        - Important people (e.g., "Albert Einstein", "Charles Darwin")
        - Key terms (e.g., "Natural Selection", "Relativity")
        - Significant places or events (e.g., "Industrial Revolution", "Renaissance")
        
        Do not include:
        - The main topic itself
        - Very common words like "research", "study", "analysis"
        - Generic terms like "method", "process", "system"
        
        IMPORTANT: Return ONLY the concept names, one per line, with no additional text or formatting.
        """
        
        try:
            print("DEBUG: Sending request to AI for concept identification...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at identifying key concepts that should be wiki-linked in research notes. Return only concept names, one per line."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            concepts_text = response.choices[0].message.content.strip()
            print(f"DEBUG: AI response: {repr(concepts_text)}")
            
            if not concepts_text:
                print("DEBUG: No concepts identified by AI")
                return content
            
            # Parse the concepts
            concepts = [concept.strip() for concept in concepts_text.split('\n') if concept.strip()]
            print(f"DEBUG: Parsed {len(concepts)} concepts: {concepts}")
            
            # Filter out concepts that already exist as files
            new_concepts = [concept for concept in concepts if concept not in existing_files]
            print(f"DEBUG: After filtering existing files, {len(new_concepts)} new concepts: {new_concepts}")
            
            if not new_concepts:
                print("DEBUG: No new concepts to link")
                return content
            
            # Convert content to wiki links
            processed_content = content
            replacements_made = 0
            
            for concept in new_concepts:
                # Use word boundaries to avoid partial matches
                # Escape special regex characters in the concept
                escaped_concept = re.escape(concept)
                pattern = r'\b' + escaped_concept + r'\b'
                
                # Count matches before replacement
                matches = re.findall(pattern, processed_content, flags=re.IGNORECASE)
                if matches:
                    print(f"DEBUG: Found {len(matches)} matches for concept '{concept}'")
                    
                    # Only replace if it's not already a wiki link
                    def replace_with_link(match):
                        matched_text = match.group(0)
                        # Check if this is already within a wiki link
                        start_pos = match.start()
                        # Look backwards to see if we're inside a wiki link
                        before_text = processed_content[:start_pos]
                        if before_text.count('[[') > before_text.count(']]'):
                            # We're inside a wiki link, don't replace
                            return matched_text
                        
                        # Use sanitized concept name to ensure consistency with filenames
                        sanitized_concept = self.sanitize_filename(concept).replace('.md', '')
                        return f'[[{sanitized_concept}]]'
                    
                    processed_content = re.sub(pattern, replace_with_link, processed_content, flags=re.IGNORECASE)
                    replacements_made += len(matches)
                else:
                    print(f"DEBUG: No matches found for concept '{concept}'")
            
            print(f"DEBUG: Made {replacements_made} total replacements")
            return processed_content
            
        except Exception as e:
            print(f"Error identifying key concepts: {e}")
            import traceback
            traceback.print_exc()
            return content

    def add_to_queue(self, concepts):
        """Add new concepts to the queue file"""
        queue_path = Path("queue.txt")
        
        # Read existing queue
        existing_queue = []
        if queue_path.exists():
            with open(queue_path, 'r') as f:
                existing_queue = [line.strip() for line in f if line.strip()]
        
        print(f"DEBUG: Existing queue: {existing_queue}")
        print(f"DEBUG: Adding concepts to queue: {concepts}")
        
        # Add new concepts (these should be exact matches to wiki link contents)
        added_count = 0
        for concept in concepts:
            if concept and concept not in existing_queue:
                existing_queue.append(concept)
                added_count += 1
                print(f"DEBUG: Added '{concept}' to queue")
        
        # Write back to queue
        with open(queue_path, 'w') as f:
            for concept in existing_queue:
                f.write(f"{concept}\n")
        
        print(f"DEBUG: Added {added_count} new concepts to queue")
        print(f"DEBUG: Total queue size: {len(existing_queue)}")

    def verify_queue_filename_consistency(self, concepts):
        """Verify that queue entries will match future filenames exactly"""
        print("DEBUG: Verifying queue-filename consistency...")
        for concept in concepts:
            if concept:
                # This is what the filename will be (without .md extension)
                future_filename = self.sanitize_filename(concept).replace('.md', '')
                print(f"DEBUG: Concept '{concept}' -> Future filename '{future_filename}' -> Match: {concept == future_filename}")
                if concept != future_filename:
                    print(f"WARNING: Concept '{concept}' will not match filename '{future_filename}'")

    def run(self, topic):
        """Main research process"""
        print(f"Starting deep research on: {topic}")
        
        # Step 1: Research the topic
        research_content = self.research_topic(topic)
        if not research_content:
            print("Failed to research topic")
            return False
        
        # Step 2: Identify and link key concepts throughout the content
        print("Identifying key concepts for wiki linking...")
        research_content = self.identify_and_link_key_concepts(research_content, topic)
        
        # Step 3: Find existing links first
        existing_links = self.find_existing_links(research_content)
        if existing_links:
            print(f"Found relevant existing notes: {existing_links}")
        
        # Step 4: Create the note with existing links
        filepath = self.create_note(topic, research_content, existing_links)
        print(f"Created note: {filepath}")
        
        # Step 5: Extract new concepts for queue
        new_concepts = self.extract_wiki_links(research_content)
        if new_concepts:
            # Verify that queue entries will match future filenames exactly
            self.verify_queue_filename_consistency(new_concepts)
            self.add_to_queue(new_concepts)
            print(f"Added to queue: {new_concepts}")
        
        print("Research completed successfully!")
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python deep_research.py <topic>")
        sys.exit(1)
    
    topic = sys.argv[1]
    
    try:
        researcher = DeepResearch()
        researcher.run(topic)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
