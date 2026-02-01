"""
Deployment Preparation Script
Prepares your project for deployment to Streamlit Cloud
"""

import os
from pathlib import Path
import shutil


def create_requirements_txt():
    """Create requirements.txt with exact versions"""
    
    requirements = """streamlit==1.30.0
langchain==0.1.0
langchain-groq==0.0.1
langchain-community==0.0.13
chromadb==0.4.22
sentence-transformers==2.3.1
python-dotenv==1.0.0
pandas==2.1.4
beautifulsoup4==4.12.3
requests==2.31.0
lxml==5.1.0
tabulate==0.9.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Created requirements.txt")


def create_gitignore():
    """Create .gitignore file"""
    
    gitignore = """# Environment
.env
venv/
env/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Jupyter
.ipynb_checkpoints

# Data (large files)
data/raw/*.csv
data/raw/*.json
*.db

# ChromaDB (will rebuild on deployment)
data/vector_db/chroma_db/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore)
    
    print("✅ Created .gitignore")


def create_streamlit_config():
    """Create Streamlit configuration"""
    
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    config = """[theme]
primaryColor="#FF6B6B"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"

[server]
headless = true
port = 8501
"""
    
    with open(streamlit_dir / "config.toml", "w") as f:
        f.write(config)
    
    print("✅ Created Streamlit config")


def create_readme():
    """Create README.md"""
    
    readme = """# 🍽️ Jaisalmer Restaurant Guide

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
source venv/bin/activate  # or `venv\\Scripts\\activate` on Windows

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
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    
    print("✅ Created README.md")


def create_secrets_template():
    """Create secrets template for Streamlit Cloud"""
    
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    secrets_example = """# This is a template
# On Streamlit Cloud, add your actual API key in the Secrets section

GROQ_API_KEY = "your_groq_api_key_here"
"""
    
    with open(streamlit_dir / "secrets.toml.example", "w") as f:
        f.write(secrets_example)
    
    print("✅ Created secrets template")


def check_data_files():
    """Check if required data files exist"""
    
    print("\n📊 Checking data files...")
    
    required_files = [
        "data/processed/cleaned_dataset.json",
        "data/processed/documents.json",
    ]
    
    missing = []
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (MISSING)")
            missing.append(file)
    
    if missing:
        print("\n⚠️  Missing required files. Run data preparation scripts first!")
        return False
    
    return True


def main():
    """Main deployment preparation"""
    
    print("="*60)
    print("DEPLOYMENT PREPARATION")
    print("="*60)
    
    print("\n📝 Creating deployment files...")
    
    create_requirements_txt()
    create_gitignore()
    create_streamlit_config()
    create_readme()
    create_secrets_template()
    
    if check_data_files():
        print("\n" + "="*60)
        print("✅ DEPLOYMENT FILES READY!")
        print("="*60)
        
        print("\n📋 Next steps:")
        print("1. Test your app locally: streamlit run src/rag/app.py")
        print("2. Create GitHub repository")
        print("3. Push code to GitHub")
        print("4. Deploy on Streamlit Cloud")
        
        print("\n⚠️  IMPORTANT:")
        print("- Don't commit .env file (it's in .gitignore)")
        print("- Add GROQ_API_KEY in Streamlit Cloud secrets")
        print("- The vector DB will be rebuilt on first deployment")
    else:
        print("\n❌ Cannot proceed. Fix missing files first.")


if __name__ == "__main__":
    main()
