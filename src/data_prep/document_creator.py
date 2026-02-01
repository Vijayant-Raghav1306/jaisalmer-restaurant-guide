"""
Document Creator
Converts cleaned data into LangChain Document objects
Handles chunking of long reviews
"""

import json
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.scraper.utils import save_json, load_json


class DocumentCreator:
    """Create Document objects from cleaned data"""
    
    def __init__(self, input_file):
        self.input_file = input_file
        self.data = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Max characters per chunk
            chunk_overlap=50,  # Overlap between chunks
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.stats = {
            "total_reviews": 0,
            "total_documents": 0,
            "chunks_created": 0
        }
    
    def load_data(self):
        """Load cleaned dataset"""
        print("="*60)
        print("DOCUMENT CREATOR")
        print("="*60)
        
        print(f"\n📂 Loading data from: {self.input_file}")
        self.data = load_json(self.input_file)
        
        if not self.data:
            raise Exception("Could not load cleaned data")
        
        restaurants = self.data.get("restaurants", [])
        total_reviews = sum(len(r.get("reviews", [])) for r in restaurants)
        
        print(f"✅ Loaded: {len(restaurants)} restaurants")
        print(f"✅ Total reviews: {total_reviews}")
        
        self.stats["total_reviews"] = total_reviews
    
    def create_document_from_review(self, review, restaurant):
        """
        Create a Document object from a review
        
        Returns:
            List of Document objects (might be multiple if chunked)
        """
        text = review.get("text", "")
        
        # Create metadata
        metadata = {
            "restaurant": restaurant.get("name", "Unknown"),
            "rating": review.get("rating", 0),
            "author": review.get("author", "Anonymous"),
            "date": review.get("date", ""),
            "source": review.get("source", "unknown"),
            "cuisine": ", ".join(restaurant.get("cuisine", [])),
            "price_range": restaurant.get("price_range", "₹₹"),
            "restaurant_rating": restaurant.get("rating", 0)
        }
        
        # Check if review needs chunking
        if len(text) > 600:
            # Split long review into chunks
            chunks = self.text_splitter.split_text(text)
            self.stats["chunks_created"] += len(chunks) - 1
            
            documents = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_index"] = i
                chunk_metadata["total_chunks"] = len(chunks)
                
                doc = Document(
                    page_content=chunk,
                    metadata=chunk_metadata
                )
                documents.append(doc)
            
            return documents
        else:
            # Single document
            doc = Document(
                page_content=text,
                metadata=metadata
            )
            return [doc]
    
    def create_all_documents(self):
        """Create documents from all reviews"""
        print("\n" + "="*60)
        print("CREATING DOCUMENTS")
        print("="*60)
        
        all_documents = []
        
        if not self.data:
            raise Exception("Data not loaded. Call load_data() first.")
        
        for restaurant in self.data.get("restaurants", []):
            rest_name = restaurant.get("name", "Unknown")
            reviews = restaurant.get("reviews", [])
            
            print(f"\n📝 {rest_name}:")
            
            for review in reviews:
                docs = self.create_document_from_review(review, restaurant)
                all_documents.extend(docs)
                
                if len(docs) > 1:
                    print(f"  ✂️  Split into {len(docs)} chunks")
                else:
                    print(f"  ✅ Created 1 document")
        
        self.stats["total_documents"] = len(all_documents)
        
        return all_documents
    
    def documents_to_dict(self, documents):
        """Convert Document objects to dictionary format for saving"""
        doc_dicts = []
        
        for doc in documents:
            doc_dict = {
                "page_content": doc.page_content,
                "metadata": doc.metadata
            }
            doc_dicts.append(doc_dict)
        
        return doc_dicts
    
    def create(self):
        """Main document creation process"""
        # Load data
        self.load_data()
        
        # Create documents
        documents = self.create_all_documents()
        
        # Print statistics
        print("\n" + "="*60)
        print("DOCUMENT STATISTICS")
        print("="*60)
        print(f"\nOriginal reviews: {self.stats['total_reviews']}")
        print(f"Total documents created: {self.stats['total_documents']}")
        print(f"Long reviews chunked: {self.stats['chunks_created']}")
        print(f"\nAvg documents per review: {self.stats['total_documents'] / self.stats['total_reviews']:.2f}")
        print("="*60)
        
        return documents


def main():
    """Main execution"""
    
    input_file = "data/processed/cleaned_dataset.json"
    output_file = "data/processed/documents.json"
    
    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        print("\nMake sure you've run:")
        print("python src/data_prep/data_cleaner.py")
        return
    
    # Create document creator
    creator = DocumentCreator(input_file)
    
    # Create documents
    documents = creator.create()
    
    # Convert to dict format for saving
    doc_dicts = creator.documents_to_dict(documents)
    
    # Save
    output_data = {
        "metadata": {
            "total_documents": len(documents),
            "source_file": input_file
        },
        "documents": doc_dicts
    }
    
    save_json(output_data, output_file)
    
    print(f"\n✅ Documents saved to: {output_file}")
    print(f"✅ Ready for embedding!")
    print("\n⏭️  Next step: Create vector database")


if __name__ == "__main__":
    main()
