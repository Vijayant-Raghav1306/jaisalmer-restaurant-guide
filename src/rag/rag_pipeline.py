"""
RAG Pipeline Core
Combines retrieval and generation into a complete Q&A system
"""

import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

from pydantic import SecretStr

# Load environment
load_dotenv()


class JaisalmerRAG:
    """Complete RAG system for Jaisalmer restaurant recommendations"""
    
    def __init__(self, persist_directory="data/vector_db/chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = None
        self.vectordb = None
        self.retriever = None
        self.llm = None
        self.qa_chain = None
        
    def initialize_embeddings(self):
        """Initialize embedding model"""
        print("📥 Loading embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ Embeddings ready")
    
    def load_vector_database(self):
        """Load the vector database"""
        print("📂 Loading vector database...")
        self.vectordb = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="jaisalmer_reviews"
        )
        print(f"✅ Database loaded ({self.vectordb._collection.count()} documents)")
    
    def setup_retriever(self, k=5, search_type="mmr"):
        """
        Setup the retriever
        
        Args:
            k: Number of documents to retrieve
            search_type: "similarity" or "mmr" (maximal marginal relevance)
        """
        print(f"🔍 Setting up retriever (k={k}, type={search_type})...")

        if self.vectordb is None:
            raise ValueError("Vector database is not loaded. Call load_vector_database() before setup_retriever().")
        
        if search_type == "mmr":
            # MMR: More diverse results
            self.retriever = self.vectordb.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": k,
                    "fetch_k": k * 4  # Fetch more, then diversify
                }
            )
        else:
            # Simple similarity
            self.retriever = self.vectordb.as_retriever(
                search_kwargs={"k": k}
            )
        
        print("✅ Retriever ready")
    
    def initialize_llm(self, model="llama-3.3-70b-versatile", temperature=0.3):
        """
        Initialize Groq LLM
        
        Args:
            model: Groq model to use
            temperature: 0 = deterministic, 1 = creative
        """
        print(f"🤖 Initializing LLM ({model})...")
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
            max_tokens=1000
        )
        
        print("✅ LLM ready")
    
    def create_prompt_template(self):
        """Create the prompt template for RAG"""
        
        template = """You are a helpful and knowledgeable restaurant guide for Jaisalmer, India. 
You help tourists find the best places to eat based on authentic customer reviews.

Context (Customer Reviews):
{context}

Question: {question}

Instructions for your answer:
1. Recommend 2-3 specific restaurants that best match the query
2. Mention specific dishes mentioned in the reviews
3. Include the price range (₹, ₹₹, or ₹₹₹) and cuisine type
4. Be concise but informative - aim for 3-5 sentences
5. Only use information from the reviews provided above
6. If the reviews don't contain relevant information, say "I don't have enough information about that in the available reviews."
7. Do not make up information or use knowledge not in the reviews

Answer format:
- Start with a direct answer to the question
- List restaurants with their key features
- Keep it natural and conversational

Answer:"""

        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def setup_qa_chain(self):
        """Create the complete RAG chain"""
        print("⛓️  Building RAG chain...")
        
        prompt = self.create_prompt_template()
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # Stuff all retrieved docs into prompt
            retriever=self.retriever,
            return_source_documents=True,  # Return sources for citation
            chain_type_kwargs={"prompt": prompt}
        )
        
        print("✅ RAG chain ready")
    
    def initialize(self):
        """Initialize the complete RAG system"""
        print("="*60)
        print("INITIALIZING JAISALMER RAG SYSTEM")
        print("="*60)
        
        self.initialize_embeddings()
        self.load_vector_database()  # Ensure vector DB is loaded before retriever
        self.setup_retriever(k=5, search_type="mmr")
        self.initialize_llm()
        self.setup_qa_chain()
        
        print("\n" + "="*60)
        print("🎉 RAG SYSTEM READY!")
        print("="*60)
    
    def query(self, question):
        """
        Ask a question and get an answer
        
        Args:
            question: User's question
            
        Returns:
            dict with 'answer' and 'source_documents'
        """
        if not self.qa_chain:
            raise ValueError("RAG system not initialized. Call initialize() first.")
        
        # Get response
        response = self.qa_chain.invoke({"query": question})
        
        return {
            "answer": response["result"],
            "source_documents": response["source_documents"]
        }
    
    def format_sources(self, source_documents):
        """Format source documents for display"""
        formatted_sources = []
        
        for i, doc in enumerate(source_documents, 1):
            source = {
                "index": i,
                "restaurant": doc.metadata.get("restaurant", "Unknown"),
                "rating": doc.metadata.get("rating", "N/A"),
                "cuisine": doc.metadata.get("cuisine", "N/A"),
                "price": doc.metadata.get("price_range", "N/A"),
                "text": doc.page_content,
                "author": doc.metadata.get("author", "Anonymous"),
                "date": doc.metadata.get("date", "N/A")
            }
            formatted_sources.append(source)
        
        return formatted_sources


def main():
    """Demo the RAG system"""
    
    print("\n" + "="*60)
    print("JAISALMER RESTAURANT RAG DEMO")
    print("="*60)
    
    # Initialize system
    rag = JaisalmerRAG()
    rag.initialize()
    
    # Test queries
    test_queries = [
        "What are the best vegetarian restaurants?",
        "Where can I find authentic Rajasthani food?",
        "Recommend budget-friendly places to eat",
        "Which restaurants have rooftop seating with views?"
    ]
    
    print("\n" + "="*60)
    print("TESTING QUERIES")
    print("="*60)
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Q: {query}")
        print('='*60)
        
        result = rag.query(query)
        
        print(f"\n💡 Answer:\n{result['answer']}")
        
        print(f"\n📚 Sources ({len(result['source_documents'])}):")
        sources = rag.format_sources(result['source_documents'])
        for source in sources[:3]:  # Show first 3
            print(f"\n{source['index']}. {source['restaurant']} ({source['rating']}⭐)")
            print(f"   {source['text'][:100]}...")
        
        print("\n" + "-"*60)
        input("Press Enter for next question...")
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
