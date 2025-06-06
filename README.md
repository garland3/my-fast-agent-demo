# Fast Ollama Agent

A Python-based AI agent that combines web search capabilities with language model processing to research topics, generate content, and perform various text operations.

## Features

- **Web Search Integration**: Uses Tavily API for intelligent web search
- **AI Processing**: Powered by Groq for fast language model inference
- **Content Generation**: Research topics and generate poems, summaries, and encoded text
- **File Operations**: Automatically saves generated content to specified files

## Prerequisites

You'll need API keys for:
- **Groq**: For language model processing
- **Tavily**: For web search functionality

## Setup

1. **Create virtual environment**:
   ```bash
   uv venv venv --python=python3.12
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Create a `.env` file with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

## Usage

Run the agent with a prompt describing your task:

```bash
python main.py -p "search for info on new mexico turtles. write a poem, then encode it. Write the unencoded poem to a file called my_poem.txt and then the encoded poem to another file called my_poem_encoded.txt"
```

## Optional: Remote Ollama Connection

If you want to connect to a remote Ollama instance instead of running locally:

```bash
ssh -L 11434:localhost:11434 user@server
```

Then on the remote server:
```bash
ollama run qwen3:0.6b
```

## Project Structure

- `main.py` - Main application entry point
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (API keys)
- `help.py` - Helper functions and utilities
- `test_*.py` - Test files for various components
- `mysearch2.py` - Web search functionality
