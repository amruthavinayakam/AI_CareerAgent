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
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('research_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize API clients
logger.info("Initializing API clients...")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
logger.info("API clients initialized successfully")

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
        logger.info("Initializing ResearchAgent...")
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory="chroma_db",
            collection_name=f"research_{int(time.time())}"
        )
        self.visited_urls = set()
        self.base_url = "https://roadmap.sh"
        logger.info("ResearchAgent initialized successfully")
        
    def search_web(self, query: str) -> str:
        """Search the web using SERP API"""
        logger.info(f"Starting web search for query: {query}")
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": os.getenv("SERP_API_KEY"),
                "num": 5
            }
            logger.info("Making SERP API request...")
            search = GoogleSearch(params)
            results = search.get_dict()
            
            formatted_results = {
                "organic_results": results.get("organic_results", []),
                "knowledge_graph": results.get("knowledge_graph", {}),
                "related_questions": results.get("related_questions", [])
            }
            
            logger.info(f"Web search completed. Found {len(formatted_results['organic_results'])} results")
            return json.dumps(formatted_results, indent=2)
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            return f"Error searching web: {str(e)}"
    
    def scrape_roadmap(self, path: str = "") -> dict:
        """Scrape roadmap.sh content and follow relevant hyperlinks"""
        url = urljoin(self.base_url, path)
        logger.info(f"Starting to scrape roadmap.sh: {url}")
        
        if url in self.visited_urls:
            logger.info(f"URL already visited: {url}")
            return {}
            
        self.visited_urls.add(url)
        try:
            logger.info(f"Making HTTP request to {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            logger.info("Parsing HTML content...")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'text': ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]),
                'roadmaps': [],
                'guides': []
            }
            
            logger.info("Extracting roadmaps...")
            roadmap_links = soup.find_all('a', href=re.compile(r'/roadmaps/'))
            for link in roadmap_links:
                href = link.get('href')
                if href and href.startswith('/roadmaps/'):
                    content['roadmaps'].append({
                        'title': link.get_text().strip(),
                        'url': urljoin(self.base_url, href)
                    })
            
            logger.info("Extracting guides...")
            guide_links = soup.find_all('a', href=re.compile(r'/guides/'))
            for link in guide_links:
                href = link.get('href')
                if href and href.startswith('/guides/'):
                    content['guides'].append({
                        'title': link.get_text().strip(),
                        'url': urljoin(self.base_url, href)
                    })
            
            logger.info(f"Successfully scraped {url}. Found {len(content['roadmaps'])} roadmaps and {len(content['guides'])} guides")
            return content
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {}
    
    def search_roadmap(self, query: str) -> str:
        """Search through roadmap.sh content based on query"""
        logger.info(f"Starting roadmap.sh search for query: {query}")
        try:
            logger.info("Getting main page content...")
            main_content = self.scrape_roadmap()
            
            relevant_content = []
            logger.info("Searching through roadmaps...")
            for roadmap in main_content.get('roadmaps', []):
                if query.lower() in roadmap['title'].lower():
                    logger.info(f"Found matching roadmap: {roadmap['title']}")
                    roadmap_content = self.scrape_roadmap(roadmap['url'])
                    if roadmap_content:
                        relevant_content.append({
                            'type': 'roadmap',
                            'title': roadmap['title'],
                            'content': roadmap_content['text']
                        })
            
            logger.info("Searching through guides...")
            for guide in main_content.get('guides', []):
                if query.lower() in guide['title'].lower():
                    logger.info(f"Found matching guide: {guide['title']}")
                    guide_content = self.scrape_roadmap(guide['url'])
                    if guide_content:
                        relevant_content.append({
                            'type': 'guide',
                            'title': guide['title'],
                            'content': guide_content['text']
                        })
            
            logger.info(f"Roadmap search completed. Found {len(relevant_content)} relevant items")
            return json.dumps(relevant_content, indent=2)
            
        except Exception as e:
            logger.error(f"Error in roadmap search: {str(e)}")
            return f"Error searching roadmap: {str(e)}"
    
    def combine_search_results(self, query: str) -> str:
        """Combine results from both SERP API and roadmap.sh"""
        logger.info(f"Starting combined search for query: {query}")
        try:
            logger.info("Getting web search results...")
            web_results = json.loads(self.search_web(query))
            
            logger.info("Getting roadmap.sh results...")
            roadmap_results = json.loads(self.search_roadmap(query))
            
            combined_results = {
                "web_search": web_results,
                "roadmap_sh": roadmap_results
            }
            
            logger.info("Successfully combined search results")
            return json.dumps(combined_results, indent=2)
        except Exception as e:
            logger.error(f"Error combining search results: {str(e)}")
            return f"Error combining search results: {str(e)}"
    
    def store_information(self, text: str):
        """Store information in the vector database"""
        logger.info("Storing information in vector database...")
        try:
            self.vector_store.add_texts([text])
            logger.info("Successfully stored information")
        except Exception as e:
            logger.error(f"Error storing information: {str(e)}")
            self.vector_store = Chroma(
                embedding_function=embeddings,
                persist_directory="chroma_db",
                collection_name=f"research_{int(time.time())}"
            )
            self.vector_store.add_texts([text])
            logger.info("Successfully stored information after retry")
    
    def retrieve_information(self, query: str) -> List[str]:
        """Retrieve relevant information from the vector database"""
        logger.info(f"Retrieving information for query: {query}")
        try:
            docs = self.vector_store.similarity_search(query)
            logger.info(f"Successfully retrieved {len(docs)} documents")
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.error(f"Error retrieving information: {str(e)}")
            return []

def main():
    logger.info("Starting application...")
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
    st.markdown('<div class="subtitle-text">Comprehensive career guidance from multiple sources</div>', unsafe_allow_html=True)
    
    # Initialize the research agent
    logger.info("Initializing research agent...")
    agent = ResearchAgent()
    
    # Create two columns for input and results
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🔍 Career Query")
        query = st.text_input("Query", placeholder="e.g., Data Science, Software Engineering, Digital Marketing")
        
        if st.button("Get Career Insights"):
            if not query:
                st.warning("Please enter a career query to get started.")
            else:
                logger.info(f"User submitted query: {query}")
                st.session_state['button_clicked'] = True
    
    with col2:
        if query and st.session_state.get('button_clicked', False):
            with st.spinner("🔍 Researching career opportunities from multiple sources..."):
                logger.info("Starting research process...")
                # Get combined results from both sources
                search_results = agent.combine_search_results(query)
                
                # Store the results
                agent.store_information(search_results)
                
                # Generate a summary using the LLM with structured prompt
                logger.info("Generating summary with LLM...")
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
                
                logger.info("Successfully generated summary")
                
                # Display results in a beautiful box
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown("### 📊 Career Insights")
                st.markdown(summary)
                st.markdown('</div>', unsafe_allow_html=True)
                logger.info("Results displayed successfully")

if __name__ == "__main__":
    main() 