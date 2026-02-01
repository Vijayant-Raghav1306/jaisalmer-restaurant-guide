"""
Experiment 1: Understanding Embeddings
Goal: See what embeddings actually look like
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load environment
load_dotenv()

print("="*60)
print("EXPERIMENT 1: What Are Embeddings?")
print("="*60)

# We'll use a free local embedding model for this experiment
# HuggingFace's sentence-transformers is perfect for learning
print("\n📥 Loading embedding model (first time will download ~100MB)...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
print("✅ Model loaded!\n")

# Let's embed some text
text = "Trio Restaurant has amazing dal baati churma"

print(f"Original text: '{text}'")
print("\nConverting to embedding...\n")

vector = embeddings.embed_query(text)

print(f"✅ Embedding created!")
print(f"   Dimensions: {len(vector)}")
print(f"   First 10 numbers: {vector[:10]}")
print(f"   Data type: {type(vector[0])}")

print("\n" + "="*60)
print("KEY INSIGHTS:")
print("="*60)
print(f"• Each word becomes part of {len(vector)} numbers")
print(f"• These numbers capture MEANING, not just letters")
print(f"• Similar sentences will have similar number patterns")
print("="*60)

