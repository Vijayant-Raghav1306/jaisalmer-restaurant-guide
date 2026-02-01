"""
Experiment 4: Impact of K parameter
Goal: See how changing K affects retrieval quality
"""

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


print("="*60)
print("EXPERIMENT 4: Impact of K Parameter")
print("="*60)

# Create more diverse reviews
reviews = [
    "Trio Restaurant: Amazing dal baati churma, authentic Rajasthani cuisine",
    "Jaisal Italy: Best vegetarian pizza, wood-fired oven",
    "Saffron Cafe: Pure veg, excellent paneer tikka",
    "The Fort View: Stunning sunset views, average food",
    "Desert Dhani: Traditional thali, unlimited servings",
    "KB Cafe: Great coffee and wifi, good for working",
    "Natraj Dining: Budget friendly, basic Indian food",
    "Jaisal Treat: Rooftop dining, mixed reviews on food",
]

documents = [Document(page_content=text) for text in reviews]

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectordb = Chroma.from_documents(
    documents=documents,
    embedding=embeddings
)

query = "vegetarian restaurant recommendations"

print(f"\n🔍 Query: '{query}'")
print("\n" + "="*60)

for k in [1, 3, 5]:
    print(f"\nK = {k} (retrieving top {k} results):")
    print("-" * 60)
    
    results = vectordb.similarity_search(query, k=k)
    
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc.page_content}")
    
    print()

print("="*60)
print("INSIGHTS:")
print("="*60)
print("• K=1: Fast but might miss relevant results")
print("• K=3: Balanced, good for most cases")
print("• K=5: More comprehensive, but may include noise")
print("\nChoice depends on your use case!")
print("="*60)

