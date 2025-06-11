import os
import streamlit as st
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from tavily import TavilyClient
from typing import List, Union
import json

# Load environment variables
load_dotenv()

# Initialize API clients
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
llm = OpenAI(temperature=0.7)
embeddings = OpenAIEmbeddings()

class ResearchAgent:
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.vector_store = Chroma(embedding_function=embeddings, persist_directory="chroma_db")
        
    def search_web(self, query: str) -> str:
        """Search the web using Tavily API"""
        try:
            response = tavily_client.search(query=query, search_depth="advanced")
            return json.dumps(response, indent=2)
        except Exception as e:
            return f"Error searching web: {str(e)}"
    
    def store_information(self, text: str):
        """Store information in the vector database"""
        self.vector_store.add_texts([text])
    
    def retrieve_information(self, query: str) -> List[str]:
        """Retrieve relevant information from the vector database"""
        docs = self.vector_store.similarity_search(query)
        return [doc.page_content for doc in docs]

def main():
    st.title("AI Research Agent")
    st.write("Enter your research query below:")
    
    # Initialize the research agent
    agent = ResearchAgent()
    
    # Create a text input for the query
    query = st.text_input("Research Query")
    
    if st.button("Research"):
        if query:
            with st.spinner("Searching the web..."):
                # Search the web
                search_results = agent.search_web(query)
                st.write("Web Search Results:")
                st.json(search_results)
                
                # Store the results
                agent.store_information(search_results)
                
                # Generate a summary using the LLM
                summary_prompt = f"Please summarize the following research findings: {search_results}"
                summary = llm(summary_prompt)
                
                st.write("Summary:")
                st.write(summary)
        else:
            st.warning("Please enter a research query.")

if __name__ == "__main__":
    main() 