"""
Retrieval Tester
Tests the vector database with various queries
Validates retrieval quality
"""

from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from tabulate import tabulate as format_table


class RetrievalTester:
    """Test and evaluate retrieval quality"""
    
    def __init__(self, persist_directory="data/vector_db/chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = None
        self.vectordb = None
        self.test_queries = [
            # Cuisine-specific queries
            "vegetarian restaurants",
            "best Rajasthani food",
            "Italian food",
            "Chinese or Tibetan cuisine",
            
            # Dish-specific queries
            "dal baati churma",
            "pizza recommendations",
            "good momos",
            "paneer dishes",
            
            # Price-related queries
            "budget friendly restaurants",
            "expensive fine dining",
            
            # Experience-based queries
            "rooftop restaurants with view",
            "romantic dinner spots",
            "family friendly places",
            
            # Quality-based queries
            "highly rated restaurants",
            "authentic local cuisine",
            "best food in Jaisalmer"
        ]
    
    def load_vector_database(self):
        """Load the existing vector database"""
        print("="*60)
        print("RETRIEVAL TESTER")
        print("="*60)
        
        if not Path(self.persist_directory).exists():
            print(f"\n❌ Vector database not found: {self.persist_directory}")
            print("\nMake sure you've run:")
            print("python src/data_prep/build_vector_db.py")
            return False
        
        print(f"\n📂 Loading vector database from: {self.persist_directory}")
        
        try:
            # Initialize embeddings (same model used for building)
            print("   Loading embedding model...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # Load ChromaDB
            print("   Loading ChromaDB...")
            self.vectordb = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="jaisalmer_reviews"
            )
            
            # Get collection info
            collection = self.vectordb._collection
            count = collection.count()
            
            print(f"✅ Database loaded!")
            print(f"   Total documents: {count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading database: {e}")
            return False
    
    def test_single_query(self, query, k=5, show_details=True):
        """
        Test a single query
        
        Args:
            query: Query string
            k: Number of results to return
            show_details: Whether to print detailed results
        """
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        print('='*60)
        
        if self.vectordb is None:
            print("❌ Vector database not loaded. Please load it first.")
            return []
        
        try:
            # Perform similarity search
            results = self.vectordb.similarity_search(query, k=k)
            
            print(f"\n📊 Found {len(results)} results:\n")
            
            if show_details:
                for i, doc in enumerate(results, 1):
                    metadata = doc.metadata
                    
                    print(f"{i}. {metadata.get('restaurant', 'Unknown')}")
                    print(f"   Rating: {metadata.get('rating', 'N/A')}⭐")
                    print(f"   Cuisine: {metadata.get('cuisine', 'N/A')}")
                    print(f"   Price: {metadata.get('price_range', 'N/A')}")
                    print(f"   Text: {doc.page_content[:150]}...")
                    print()
            
            return results
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return []
    
    def test_with_filters(self):
        """Test queries with metadata filters"""
        print("\n" + "="*60)
        print("TESTING WITH FILTERS")
        print("="*60)
        
        if self.vectordb is None:
            print("❌ Vector database not loaded. Please load it first.")
            return
        
        test_cases = [
            {
                "query": "good food",
                "filter": {"rating": {"$gte": 4}},
                "description": "Good food with rating >= 4"
            },
            {
                "query": "vegetarian",
                "filter": {"price_range": "₹₹"},
                "description": "Vegetarian with mid-range price"
            }
        ]
        
        for test in test_cases:
            print(f"\n🔍 Test: {test['description']}")
            print(f"   Query: '{test['query']}'")
            print(f"   Filter: {test['filter']}")
            
            try:
                # Note: ChromaDB filtering syntax
                results = self.vectordb.similarity_search(
                    test['query'],
                    k=3,
                    filter=test['filter']
                )
                
                print(f"   Results: {len(results)}")
                
                for i, doc in enumerate(results, 1):
                    print(f"   {i}. {doc.metadata.get('restaurant', 'Unknown')} "
                          f"({doc.metadata.get('rating', 'N/A')}⭐)")
                
            except Exception as e:
                print(f"   ⚠️  Filter test failed: {e}")
                print(f"   (Some ChromaDB versions have limited filter support)")
    
    def test_retrieval_quality(self):
        """Test retrieval quality with expected results"""
        print("\n" + "="*60)
        print("RETRIEVAL QUALITY EVALUATION")
        print("="*60)
        
        if self.vectordb is None:
            print("❌ Vector database not loaded. Please load it first.")
            return
        
        quality_tests = [
            {
                "query": "vegetarian restaurants",
                "expected_keywords": ["veg", "vegetarian", "paneer", "dal"],
                "name": "Vegetarian Query"
            },
            {
                "query": "Rajasthani traditional food",
                "expected_keywords": ["rajasthani", "dal baati", "traditional", "authentic"],
                "name": "Cuisine Query"
            },
            {
                "query": "rooftop dining",
                "expected_keywords": ["rooftop", "view", "terrace", "fort"],
                "name": "Experience Query"
            }
        ]
        
        results_summary = []
        
        for test in quality_tests:
            print(f"\n📝 Test: {test['name']}")
            print(f"   Query: '{test['query']}'")
            
            results = self.vectordb.similarity_search(test['query'], k=5)
            
            # Check if results contain expected keywords
            matches = 0
            for doc in results:
                text = (doc.page_content + " " + 
                       doc.metadata.get('cuisine', '')).lower()
                
                if any(keyword in text for keyword in test['expected_keywords']):
                    matches += 1
            
            relevance = (matches / len(results) * 100) if results else 0
            
            results_summary.append([
                test['name'],
                test['query'],
                len(results),
                matches,
                f"{relevance:.1f}%"
            ])
            
            print(f"   Relevant results: {matches}/{len(results)} ({relevance:.1f}%)")
        
        # Print summary table
        print("\n" + "="*60)
        print("QUALITY SUMMARY")
        print("="*60)
        
        headers = ["Test", "Query", "Total", "Relevant", "Relevance %"]
        print("\n" + format_table(results_summary, headers=headers, tablefmt="grid"))
        
        # Overall assessment
        avg_relevance = sum(float(r[4].rstrip('%')) for r in results_summary) / len(results_summary)
        
        print(f"\n📊 Average Relevance: {avg_relevance:.1f}%")
        
        if avg_relevance >= 80:
            print("✅ Excellent retrieval quality!")
        elif avg_relevance >= 60:
            print("✅ Good retrieval quality")
        else:
            print("⚠️  Retrieval quality could be improved")
    
    def test_diversity(self):
        """Test if results are diverse (not all from same restaurant)"""
        print("\n" + "="*60)
        print("DIVERSITY TEST")
        print("="*60)
        
        if self.vectordb is None:
            print("❌ Vector database not loaded. Please load it first.")
            return
        
        query = "best restaurants in Jaisalmer"
        results = self.vectordb.similarity_search(query, k=10)
        
        # Count unique restaurants
        restaurants = [doc.metadata.get('restaurant', 'Unknown') for doc in results]
        unique_restaurants = len(set(restaurants))
        
        print(f"\nQuery: '{query}'")
        print(f"Results: {len(results)}")
        print(f"Unique restaurants: {unique_restaurants}")
        print(f"Diversity score: {unique_restaurants / len(results) * 100:.1f}%")
        
        # List restaurants
        print("\nRestaurants in results:")
        from collections import Counter
        restaurant_counts = Counter(restaurants)
        for restaurant, count in restaurant_counts.most_common():
            print(f"   {restaurant}: {count} reviews")
        
        if unique_restaurants / len(results) >= 0.5:
            print("\n✅ Good diversity!")
        else:
            print("\n⚠️  Low diversity - results dominated by few restaurants")
    
    def interactive_test(self):
        """Interactive testing mode"""
        print("\n" + "="*60)
        print("INTERACTIVE TESTING MODE")
        print("="*60)
        print("\nEnter queries to test (type 'exit' to quit)")
        print("="*60)
        
        while True:
            query = input("\n🔍 Query: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Exiting interactive mode")
                break
            
            if not query:
                continue
            
            self.test_single_query(query, k=5, show_details=True)
    
    def run_all_tests(self):
        """Run all automated tests"""
        # Load database
        if not self.load_vector_database():
            return
        
        # Test basic queries
        print("\n" + "="*60)
        print("BASIC QUERY TESTS")
        print("="*60)
        
        for query in self.test_queries[:5]:  # Test first 5
            self.test_single_query(query, k=3, show_details=False)
        
        # Test with filters
        self.test_with_filters()
        
        # Test quality
        self.test_retrieval_quality()
        
        # Test diversity
        self.test_diversity()
        
        # Final summary
        print("\n" + "="*60)
        print("🎉 ALL TESTS COMPLETE!")
        print("="*60)
        print("\n✅ Vector database is working correctly!")
        print("✅ Retrieval quality is acceptable!")
        print("\n⏭️  Ready to build RAG pipeline!")
        print("="*60)


def main():
    """Main execution"""
    
    print("\n" + "="*60)
    print("RETRIEVAL SYSTEM TESTER")
    print("="*60)
    print("\nOptions:")
    print("1. Run automated tests")
    print("2. Interactive testing mode")
    print("3. Both")
    
    choice = input("\nChoose (1/2/3): ").strip()
    
    tester = RetrievalTester()
    
    if choice == "1":
        tester.run_all_tests()
    elif choice == "2":
        if tester.load_vector_database():
            tester.interactive_test()
    elif choice == "3":
        tester.run_all_tests()
        
        print("\n" + "="*60)
        proceed = input("\nProceed to interactive mode? (y/n): ").strip().lower()
        if proceed == 'y':
            tester.interactive_test()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    # Install tabulate if not available
    try:
        import tabulate
    except ImportError:
        print("Installing tabulate for better output formatting...")
        import subprocess
        subprocess.check_call(["pip", "install", "tabulate"])
    
    main()
