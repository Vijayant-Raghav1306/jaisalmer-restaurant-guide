"""
Experiment 3: Complete Mini RAG Pipeline (FIXED VERSION)
Goal: Build a tiny working RAG system with fake data
"""

import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# Load environment
load_dotenv()

print("="*60)
print("EXPERIMENT 3: Mini RAG System (FIXED)")
print("="*60)

# Step 1: Create fake restaurant reviews (our "knowledge base")
fake_reviews = [
    {
        "text": "Trio Restaurant serves amazing dal baati churma with authentic Rajasthani flavors. The rooftop seating offers a beautiful view of the fort.",
        "restaurant": "Trio Restaurant",
        "cuisine": "Rajasthani",
    },
    {
        "text": "Jaisal Italy has the best wood-fired pizza in Jaisalmer. Great vegetarian options including margherita and mushroom pizza.",
        "restaurant": "Jaisal Italy",
        "cuisine": "Italian",
    },
    {
        "text": "Saffron Cafe is a pure vegetarian restaurant with excellent paneer tikka and dal makhani. Very affordable prices.",
        "restaurant": "Saffron Cafe",
        "cuisine": "North Indian",
    },
    {
        "text": "The fort view from Trio Restaurant's terrace is stunning during sunset. Must visit for ambiance.",
        "restaurant": "Trio Restaurant",
        "cuisine": "Rajasthani",
    },
    {
        "text": "Desert Boy's Dhani offers traditional Rajasthani thali with unlimited servings. Great for experiencing local cuisine.",
        "restaurant": "Desert Boy's Dhani",
        "cuisine": "Rajasthani",
    },
]

print("\n📚 Created knowledge base with 5 fake reviews")

# Step 2: Convert to LangChain documents
documents = [
    Document(
        page_content=review["text"],
        metadata={
            "restaurant": review["restaurant"],
            "cuisine": review["cuisine"]
        }
    )
    for review in fake_reviews
]

print("✅ Converted to Document format")

# Step 3: Create embeddings and vector store
print("\n🔄 Creating embeddings and vector database...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectordb = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="./mini_chroma_db"
)
print("✅ Vector database created and persisted")

# Step 4: Test retrieval
print("\n" + "="*60)
print("TESTING RETRIEVAL")
print("="*60)

test_query = "What are good vegetarian options?"
print(f"\n🔍 Query: '{test_query}'")

retrieved_docs = vectordb.similarity_search(test_query, k=2)

print(f"\n📄 Top 2 Retrieved Reviews:")
for i, doc in enumerate(retrieved_docs, 1):
    print(f"\n{i}. Restaurant: {doc.metadata['restaurant']}")
    print(f"   Text: {doc.page_content[:100]}...")

# Step 5: Create RAG chain with Groq (FIXED - using updated model)
print("\n" + "="*60)
print("BUILDING RAG CHAIN")
print("="*60)

# ✅ FIXED: Using current model
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Updated model
    temperature=0.3,
    
)

print("✅ Using model: llama-3.3-70b-versatile")

template = """You are a helpful Jaisalmer restaurant guide.
Use the following reviews to answer the question.
If you don't know, say so honestly.

Reviews:
{context}

Question: {question}

Provide a helpful answer with specific restaurant names:"""

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True  # This helps us see what was retrieved
)

print("✅ RAG chain created")

# Step 6: Ask questions! (FIXED - using invoke instead of deprecated run)
print("\n" + "="*60)
print("ASKING QUESTIONS")
print("="*60)

questions = [
    "What are good vegetarian options?",
    "Where can I get authentic Rajasthani food?",
    "Any Italian restaurants?",
]

for question in questions:
    print(f"\n❓ Question: {question}")
    print("🤖 Answer: ", end="")
    
    # ✅ FIXED: Using invoke() instead of deprecated run()
    result = qa_chain.invoke({"query": question})
    response = result["result"]
    
    print(response)
    
    # Optional: Show which documents were used
    print("\n   📚 Sources used:")
    for i, doc in enumerate(result["source_documents"], 1):
        print(f"      {i}. {doc.metadata['restaurant']}")
    
    print("-" * 60)

print("\n" + "="*60)
print("🎉 MINI RAG SYSTEM COMPLETE!")
print("="*60)
print("\nWhat just happened:")
print("1. ✅ Created a knowledge base (5 reviews)")
print("2. ✅ Converted text to embeddings")
print("3. ✅ Stored in vector database (ChromaDB)")
print("4. ✅ Retrieved relevant reviews for queries")
print("5. ✅ Generated answers using Groq LLM")
print("\nThis is EXACTLY what your full system will do!")
print("Just with more data and a prettier frontend!")
print("="*60)



