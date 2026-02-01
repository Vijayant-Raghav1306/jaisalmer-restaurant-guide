"""
Vector Database Builder
Creates embeddings and loads into ChromaDB
"""

import json
from pathlib import Path
from datetime import datetime
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document



class VectorDBBuilder:
    """Build ChromaDB vector database from documents"""
    
    def __init__(self, documents_file, persist_directory="data/vector_db/chroma_db"):
        self.documents_file = documents_file
        self.persist_directory = persist_directory
        self.embeddings = None
        self.vectordb = None
        self.stats = {
            "total_documents": 0,
            "successful_embeddings": 0,
            "failed_embeddings": 0,
            "embedding_time": 0.0
        }
    
    def load_documents(self):
        """Load documents from JSON file"""
        print("="*60)
        print("VECTOR DATABASE BUILDER")
        print("="*60)
        
        print(f"\n📂 Loading documents from: {self.documents_file}")
        
        try:
            with open(self.documents_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            doc_dicts = data.get("documents", [])
            
            # Convert dict back to Document objects
            documents = []
            for doc_dict in doc_dicts:
                doc = Document(
                    page_content=doc_dict["page_content"],
                    metadata=doc_dict["metadata"]
                )
                documents.append(doc)
            
            self.stats["total_documents"] = len(documents)
            print(f"✅ Loaded {len(documents)} documents")
            
            return documents
            
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
            return None
    
    def initialize_embeddings(self):
        """Initialize the embedding model"""
        print("\n" + "="*60)
        print("INITIALIZING EMBEDDING MODEL")
        print("="*60)
        
        print("\n📥 Loading model: all-MiniLM-L6-v2")
        print("   (First time will download ~90MB)")
        
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},  # Use CPU (works everywhere)
                encode_kwargs={'normalize_embeddings': True}  # Normalize for better similarity
            )
            
            print("✅ Model loaded successfully!")
            
            # Test embedding
            print("\n🧪 Testing embedding...")
            test_text = "This is a test sentence"
            test_embedding = self.embeddings.embed_query(test_text)
            print(f"   Embedding dimensions: {len(test_embedding)}")
            print(f"   Sample values: {test_embedding[:5]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def create_vector_database(self, documents):
        """Create ChromaDB vector database"""
        print("\n" + "="*60)
        print("CREATING VECTOR DATABASE")
        print("="*60)
        
        # Create persist directory if it doesn't exist
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        print(f"\n📊 Processing {len(documents)} documents...")
        print("   This may take 30-60 seconds...")
        
        try:
            import time
            start_time = time.time()
            
            # Create ChromaDB from documents
            self.vectordb = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name="jaisalmer_reviews"
            )
            
            # Persist to disk
            self.vectordb.persist()
            
            end_time = time.time()
            self.stats["embedding_time"] = end_time - start_time
            self.stats["successful_embeddings"] = len(documents)
            
            print(f"\n✅ Vector database created!")
            print(f"   Time taken: {self.stats['embedding_time']:.2f} seconds")
            print(f"   Documents embedded: {self.stats['successful_embeddings']}")
            print(f"   Persisted to: {self.persist_directory}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    def verify_database(self):
        """Verify the database was created correctly"""
        print("\n" + "="*60)
        print("VERIFYING DATABASE")
        print("="*60)
        
        try:
            # Get collection info
            if self.vectordb is None:
                print("❌ Vector database not initialized")
                return False
            
            collection = self.vectordb._collection
            count = collection.count()
            
            print(f"\n✅ Database verification:")
            print(f"   Documents stored: {count}")
            print(f"   Collection name: jaisalmer_reviews")
            print(f"   Persist directory: {self.persist_directory}")
            
            # Test query
            print("\n🧪 Testing sample query...")
            test_query = "vegetarian food"
            results = self.vectordb.similarity_search(test_query, k=3)
            
            print(f"   Query: '{test_query}'")
            print(f"   Results found: {len(results)}")
            
            if results:
                print("\n   Top result preview:")
                top_result = results[0]
                print(f"   Restaurant: {top_result.metadata.get('restaurant', 'Unknown')}")
                print(f"   Text: {top_result.page_content[:100]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def generate_report(self):
        """Generate final report"""
        report = {
            "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "persist_directory": self.persist_directory,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_dimensions": 384,
            "statistics": self.stats
        }
        
        # Save report
        report_file = f"{self.persist_directory}/build_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "="*60)
        print("BUILD REPORT")
        print("="*60)
        print(f"\nTotal documents processed: {self.stats['total_documents']}")
        print(f"Successfully embedded: {self.stats['successful_embeddings']}")
        print(f"Failed: {self.stats['failed_embeddings']}")
        print(f"Embedding time: {self.stats['embedding_time']:.2f}s")
        print(f"Avg time per document: {self.stats['embedding_time'] / self.stats['total_documents']:.3f}s")
        print(f"\nReport saved to: {report_file}")
        print("="*60)
    
    def build(self):
        """Main build process"""
        # Load documents
        documents = self.load_documents()
        if not documents:
            return False
        
        # Initialize embeddings
        if not self.initialize_embeddings():
            return False
        
        # Create vector database
        if not self.create_vector_database(documents):
            return False
        
        # Verify
        if not self.verify_database():
            print("⚠️  Verification had issues, but database might still work")
        
        # Generate report
        self.generate_report()
        
        return True


def main():
    """Main execution"""
    
    documents_file = "data/processed/documents.json"
    persist_directory = "data/vector_db/chroma_db"
    
    if not Path(documents_file).exists():
        print(f"❌ Documents file not found: {documents_file}")
        print("\nMake sure you've run:")
        print("python src/data_prep/document_creator.py")
        return
    
    print("\n🚀 Starting vector database build...")
    print("   This will take 30-60 seconds\n")
    
    # Create builder
    builder = VectorDBBuilder(documents_file, persist_directory)
    
    # Build database
    success = builder.build()
    
    if success:
        print("\n" + "="*60)
        print("🎉 SUCCESS!")
        print("="*60)
        print("\n✅ Vector database is ready!")
        print(f"✅ Location: {persist_directory}")
        print("\n⏭️  Next step: Test retrieval system")
        print("="*60)
    else:
        print("\n❌ Build failed. Check errors above.")


if __name__ == "__main__":
    main()
