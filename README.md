# 🍽️ Jaisalmer Restaurant Guide

AI-powered restaurant recommendation system using RAG (Retrieval-Augmented Generation).

## Features

- 🤖 AI-powered Q&A about Jaisalmer restaurants
- 📚 Based on 80+ real customer reviews
- 🔍 Semantic search using vector embeddings
- 💬 Natural language interface
- 🎯 Personalized recommendations

## Tech Stack

- **Frontend:** Streamlit
- **LLM:** Groq (Llama 3.3 70B)
- **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2)
- **Vector DB:** ChromaDB
- **Framework:** LangChain

## How It Works

1. User asks a question about restaurants
2. System converts query to vector embedding
3. Retrieves relevant reviews from ChromaDB
4. Sends context + query to Groq LLM
5. Returns AI-generated personalized answer

## Local Setup
```bash
# Clone repository
git clone <your-repo-url>
cd jaisalmer-reviews

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key to .env
echo "GROQ_API_KEY=your_key_here" > .env

# Run the app
streamlit run src/rag/app.py
```

## Data Sources

- Manual collection from Google Maps
- Blog scraping from travel sites
- Public Zomato dataset (adapted)

## Project Structure
```
jaisalmer-reviews/
├── src/
│   ├── scraper/          # Data collection
│   ├── data_prep/        # Data cleaning & vectorization
│   └── rag/              # RAG pipeline & app
├── data/
│   ├── processed/        # Cleaned data
│   └── vector_db/        # ChromaDB storage
└── requirements.txt
```

## Author

Built as a learning project to understand RAG systems.

## License

MIT
