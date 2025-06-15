# 🧠 AI Career Agent

An intelligent AI-powered career assistant that combines web search capabilities with curated roadmap insights to deliver structured, role-specific career guidance. It leverages Google's Gemini model, SERP API, Chroma vector storage, and Streamlit UI for a complete Retrieval-Augmented Generation (RAG) experience.

---

## 🚀 Features

* 🔍 **Smart Web Search** via SERP API
* 📚 **Roadmap Crawler** for extracting role-specific paths from [roadmap.sh](https://roadmap.sh)
* 🤖 **AI-Powered Summarization** using Gemini 2.0 Flash
* 🧠 **Vector-Based Knowledge Storage** using ChromaDB
* 🗂️ **Context-Aware Memory** with LangChain
* 🧑‍💻 **User-Friendly Interface** built with Streamlit
* 📄 **Structured Career Guides** in markdown format
* 🛡️ Logging enabled with timestamps for observability and debugging

---

## ⚙️ Setup Instructions

1. **Clone this repository**

   ```bash
   git clone https://github.com/your-username/ai-career-agent.git
   cd ai-career-agent
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Add environment variables**
   Create a `.env` file in the root directory:

   ```
   GOOGLE_API_KEY=your_google_gemini_api_key
   SERP_API_KEY=your_serp_api_key
   ```

---

## ▶️ Usage

1. **Start the application**

   ```bash
   streamlit run research_agent.py
   ```

2. **Access the app**
   Open your browser and navigate to [http://localhost:8501](http://localhost:8501)

3. **Explore career paths**

   * Type a career or domain (e.g., "Data Scientist", "UX Designer", "Cloud Engineer")
   * Click **"Get Career Insights"**
   * The agent will:

     * Perform a live Google search
     * Crawl relevant paths on roadmap.sh
     * Combine and store the information
     * Generate a structured, beginner-friendly career guide

---

## 🧰 Requirements

* Python 3.8+
* [Google Gemini API key](https://ai.google.dev/)
* [SERP API key](https://serpapi.com/)

---

## 📁 Project Structure

| File                 | Description                               |
| -------------------- | ----------------------------------------- |
| `research_agent.py`  | Main application logic                    |
| `requirements.txt`   | Dependency list                           |
| `.env`               | Environment variables (never commit this) |
| `chroma_db/`         | Vector store persistence                  |
| `research_agent.log` | Log file capturing runtime events         |

