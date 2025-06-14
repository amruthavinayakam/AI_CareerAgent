import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from serpapi import GoogleSearch
from typing import List, Union
import json
import time

# Load environment variables
load_dotenv()

# Initialize API clients
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Define prompts
SERP_SEARCH_PROMPT = """
Please search for comprehensive career information about: {query}

Focus on retrieving:
1. Common job roles in this domain (e.g., job titles, responsibilities)
2. Technical and soft skills required for each role
3. Tools and technologies widely used in the industry
4. Recommended learning paths or roadmaps to acquire these skills
5. Companies actively hiring in this field and related industries
6. Trends in job market demand, salary, and qualifications

Use recent, authoritative sources like job boards, research publications, expert career guides, and company hiring pages.
"""

LLM_SUMMARY_PROMPT = """
You are an expert career advisor helping beginners enter the role in the field of: {query}.

Based on the following search results: {search_results}

Generate a clear, comprehensive, and structured career guide tailored for someone exploring opportunities in this domain.

Organize the output into the following **markdown-formatted sections**:

1. **Target Roles**  
   List common job titles and provide 1–2 sentence descriptions for each role.

2. **Required Skills**  
   Break down into:
   - **Technical Skills** (e.g., Python, machine learning algorithms, data analysis tools)
   - **Soft Skills** (e.g., communication, critical thinking, problem-solving)

3. **Tools & Technologies**  
   Mention specific tools used in real-world data science and ML applications.

4. **Learning Roadmap**  
   Suggest a practical step-by-step path for acquiring the necessary skills. Include relevant online courses, certifications, tutorials, and project types.

5. **Top Companies Hiring**  
   List key companies hiring in this space, including tech giants, startups, and industry-specific leaders.

6. **Industry Trends & Insights**  
   Summarize current job demand, hiring patterns, and geographic or remote work trends.

7. **Bonus Tips** (Optional)  
   Share additional advice such as portfolio-building, networking strategies, and specialization opportunities.

---

🛑 **Important Output Instructions:**
- ✅ Format the output as **clean, readable markdown or plain text**.
- ❌ Do NOT return the output in JSON, YAML, XML.
- ❌ Do NOT use code blocks (```), angle brackets, or HTML.
- ✅ Ensure the output is structured for readability, using headers and bullet points.
- ✅ Keep the tone beginner-friendly but insightful and practical.

The final response should be ready for direct display in a UI or document without any further formatting.
"""


class ResearchAgent:
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        # Create a new collection each time to avoid dimension mismatch
        self.vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory="chroma_db",
            collection_name=f"research_{int(time.time())}"  # Unique collection name
        )
        
    def search_web(self, query: str) -> str:
        """Search the web using SERP API"""
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": os.getenv("SERP_API_KEY"),
                "num": 5  # Number of results to return
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract and format relevant information
            formatted_results = {
                "organic_results": results.get("organic_results", []),
                "knowledge_graph": results.get("knowledge_graph", {}),
                "related_questions": results.get("related_questions", [])
            }
            
            return json.dumps(formatted_results, indent=2)
        except Exception as e:
            return f"Error searching web: {str(e)}"
    
    def store_information(self, text: str):
        """Store information in the vector database"""
        try:
            self.vector_store.add_texts([text])
        except Exception as e:
            st.error(f"Error storing information: {str(e)}")
            # Create a new collection if there's an error
            self.vector_store = Chroma(
                embedding_function=embeddings,
                persist_directory="chroma_db",
                collection_name=f"research_{int(time.time())}"
            )
            self.vector_store.add_texts([text])
    
    def retrieve_information(self, query: str) -> List[str]:
        """Retrieve relevant information from the vector database"""
        try:
            docs = self.vector_store.similarity_search(query)
            return [doc.page_content for doc in docs]
        except Exception as e:
            st.error(f"Error retrieving information: {str(e)}")
            return []

def main():
    # Set page config
    st.set_page_config(
        page_title="AI Career Advisor",
        page_icon="🎯",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .main {
            background-color: #ffffff;
        }
        .stButton>button {
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            border: none;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #34495e;
            transition: background-color 0.3s ease;
        }
        .title-text {
            font-size: 2.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        .subtitle-text {
            font-size: 1.2rem;
            color: #7f8c8d;
            margin-bottom: 2rem;
        }
        .result-box {
            background-color: #f8f9fa;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin: 1rem 0;
            border: 1px solid #e9ecef;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="title-text">AI Career Advisor</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Your personal guide to career exploration and development</div>', unsafe_allow_html=True)
    
    # Initialize the research agent
    agent = ResearchAgent()
    
    # Create two columns for input and results
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🔍 Career Query")
        query = st.text_input("Query", placeholder="e.g., Data Science, Software Engineering, Digital Marketing")
        
        if st.button("Get Career Insights "):
            if not query:
                st.warning("Please enter a career query to get started.")
            else:
                st.session_state['button_clicked'] = True
    
    with col2:
        if query and st.session_state.get('button_clicked', False):
            with st.spinner("🔍 Researching career opportunities..."):
                # Search the web
                search_results = agent.search_web(query)
                
                # Store the results
                agent.store_information(search_results)
                
                # Generate a summary using the LLM with structured prompt
                summary_prompt = LLM_SUMMARY_PROMPT.format(
                    query=query,
                    search_results=search_results
                )
                response = llm.invoke(summary_prompt)
                
                # Extract just the content from the response
                if isinstance(response, dict) and 'content' in response:
                    summary = response['content']
                elif hasattr(response, 'content'):
                    summary = response.content
                else:
                    summary = str(response)
                
                # Display results in a beautiful box
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown("### 📊 Career Insights")
                st.markdown(summary)
                st.markdown('</div>', unsafe_allow_html=True)    

if __name__ == "__main__":
    main() 