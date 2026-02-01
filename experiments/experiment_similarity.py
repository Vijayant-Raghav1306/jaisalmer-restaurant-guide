"""
Experiment 2: Semantic Similarity
Goal: See how similar/different sentences are in vector space
"""

import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings


print("="*60)
print("EXPERIMENT 2: Semantic Similarity")
print("="*60)

# Load model
print("\n📥 Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Test sentences
sentences = {
    "A": "Great vegetarian pizza with fresh toppings",
    "B": "Excellent veg pizza with organic ingredients",
    "C": "The fort has stunning architecture and history",
    "D": "Amazing paneer dishes and dal makhani",
}

print("\n📝 Test Sentences:")
for key, sentence in sentences.items():
    print(f"   {key}: {sentence}")

# Generate embeddings
print("\n🔄 Generating embeddings...")
vectors = {key: embeddings.embed_query(sent) 
           for key, sent in sentences.items()}

# Function to calculate cosine similarity
def cosine_similarity(v1, v2):
    """Calculate cosine similarity between two vectors"""
    v1, v2 = np.array(v1), np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# Calculate all similarities
print("\n" + "="*60)
print("SIMILARITY SCORES (0 = different, 1 = identical)")
print("="*60)

comparisons = [
    ("A", "B", "Both about vegetarian pizza"),
    ("A", "C", "Pizza vs Architecture"),
    ("A", "D", "Pizza vs Paneer (both food)"),
    ("C", "D", "Architecture vs Food"),
]

for sent1, sent2, description in comparisons:
    sim = cosine_similarity(vectors[sent1], vectors[sent2])
    bar = "█" * int(sim * 40)
    
    print(f"\n{sent1} vs {sent2}: {sim:.3f} {bar}")
    print(f"   ({description})")

print("\n" + "="*60)
print("KEY INSIGHTS:")
print("="*60)
print("• Similar topics = HIGH similarity (>0.7)")
print("• Different topics = LOW similarity (<0.4)")
print("• Same domain (food) = MEDIUM similarity (0.4-0.7)")
print("="*60)

