# AI Research Agent

An intelligent research assistant that combines web search capabilities with AI-powered analysis and information storage.

## Features

- Web search using Tavily API
- AI-powered analysis using OpenAI's GPT models
- Vector storage using ChromaDB for efficient information retrieval
- User-friendly interface built with Streamlit
- Conversation memory for context-aware interactions

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

## Usage

1. Run the Streamlit application:
   ```bash
   streamlit run research_agent.py
   ```
2. Open your web browser and navigate to the provided local URL (typically http://localhost:8501)
3. Enter your research query in the text input field
4. Click the "Research" button to start the research process

## Requirements

- Python 3.8+
- OpenAI API key
- Tavily API key

## Project Structure

- `research_agent.py`: Main application file
- `requirements.txt`: Project dependencies
- `.env`: Environment variables (API keys)

## Note

Make sure to keep your API keys secure and never commit them to version control. 