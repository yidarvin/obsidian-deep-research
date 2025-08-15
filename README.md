# Obsidian Deep Research Tool

A Python tool that uses OpenAI's o4-mini-deep-research model to create comprehensive research notes in Obsidian format. The tool automatically manages a research queue and creates interconnected notes using Obsidian's wiki-links.

## Features

- **Deep Research**: Uses OpenAI's o4-mini-deep-research model for comprehensive topic research
- **Obsidian Integration**: Creates notes in Obsidian format with proper frontmatter
- **Queue Management**: Automatically adds related concepts to a research queue
- **Smart Linking**: Finds connections between existing notes and new research
- **Template-Based**: Uses a consistent note template for organization
- **Rate Limit Aware**: Designed to be concise and avoid deep research in single sessions

## Setup

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd obsidian-deep-research

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit the `.env` file with your settings:

```env
OPENAI_API_KEY=your_openai_api_key_here
PATH_TO_SAVE=/path/to/your/obsidian/vault
```

- `OPENAI_API_KEY`: Your OpenAI API key
- `PATH_TO_SAVE`: The directory where your Obsidian vault is located

## Usage

### Basic Research

Research a single topic:

```bash
python deep_research.py "Disneyland"
```

Research a complex question:

```bash
python deep_research.py "Plan a disneyland vacation for my family with a 1 y.o. toddler"
```

### Queue Management

Process the next item in the queue:

```bash
python pop_queue.py
```

List current queue contents:

```bash
python pop_queue.py --list
```

Clear the queue:

```bash
python pop_queue.py --clear
```

## How It Works

### 1. Research Process

1. **Topic Analysis**: The tool takes your topic and sends it to OpenAI's o4-mini-deep-research model
2. **Content Generation**: Creates a comprehensive but concise research note following the template structure
3. **Wiki-Links**: Automatically adds `[[wiki-links]]` for related concepts that could be separate notes
4. **File Creation**: Saves the note with proper frontmatter in your Obsidian vault

### 2. Post-Processing

1. **Existing Links**: Scans your vault for existing notes that should be linked to the new research
2. **Queue Management**: Extracts wiki-links that don't exist yet and adds them to `queue.txt`
3. **Smart Connections**: Uses a cheaper model (gpt-4o-mini) to find relevant connections

### 3. Queue System

- New concepts discovered during research are automatically added to `queue.txt`
- Use `pop_queue.py` to process one item at a time
- This prevents overwhelming the API and allows for systematic research

## Note Structure

Each research note follows the template structure:

```markdown
---
title: "Your Topic"
aliases: []
tags: [research, your_topic]
created: "2024-01-01 12:00:00"
modified: "2024-01-01 12:00:00"
note_type: "research"
---

## Summary
Brief overview of the research

## Note Content
Key findings and information

## Action Items
- [ ] Next steps or tasks

## Questions & Learnings
### Questions
- Questions for further research

### Learnings
- Key insights discovered

## Links & References
### Related Notes
- [[Related Note 1]]
- [[Related Note 2]]

### External Links
- [Link title](https://example.com) - Description
```

## Best Practices

1. **Start Simple**: Begin with broad topics, then use the queue for deeper research
2. **Use the Queue**: Don't try to research everything at once - let the queue guide your research
3. **Review Links**: Check the generated wiki-links to ensure they make sense
4. **Iterate**: Use the queue system to build a comprehensive knowledge base over time

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your OpenAI API key is correctly set in `.env`
2. **Path Error**: Ensure `PATH_TO_SAVE` points to a valid directory
3. **Rate Limits**: The tool is designed to be concise, but if you hit limits, wait and try again
4. **Template Missing**: Ensure `Simple_Note_Template.md` is in the project root

### Debug Mode

To see more detailed output, you can modify the scripts to add debug logging.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
