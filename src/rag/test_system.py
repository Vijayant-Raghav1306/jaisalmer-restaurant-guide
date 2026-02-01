"""
Comprehensive System Tester
Tests the complete RAG system before deployment
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.rag.rag_pipeline import JaisalmerRAG
import time


class SystemTester:
    """Test the complete RAG system"""
    
    def __init__(self):
        self.rag = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "total": 0
        }
    
    def setup(self):
        """Initialize the RAG system"""
        print("="*60)
        print("SYSTEM TESTING SUITE")
        print("="*60)
        print("\n📋 Setting up RAG system...")
        
        try:
            self.rag = JaisalmerRAG()
            self.rag.initialize()
            print("✅ Setup complete\n")
            return True
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def test_case(self, name, test_func):
        """Run a single test case"""
        self.test_results["total"] += 1
        print(f"\n{'='*60}")
        print(f"Test {self.test_results['total']}: {name}")
        print('='*60)
        
        try:
            test_func()
            print(f"✅ PASSED: {name}")
            self.test_results["passed"] += 1
            return True
        except AssertionError as e:
            print(f"❌ FAILED: {name}")
            print(f"   Reason: {e}")
            self.test_results["failed"] += 1
            return False
        except Exception as e:
            print(f"❌ ERROR: {name}")
            print(f"   Error: {e}")
            self.test_results["failed"] += 1
            return False
    
    def test_basic_query(self):
        """Test basic query functionality"""
        assert self.rag is not None, "RAG system not initialized"
        query = "vegetarian restaurants"
        result = self.rag.query(query)
        
        assert result is not None, "No result returned"
        assert "answer" in result, "No answer in result"
        assert "source_documents" in result, "No sources in result"
        assert len(result["answer"]) > 0, "Empty answer"
        assert len(result["source_documents"]) > 0, "No source documents"
        
        print(f"   Query: '{query}'")
        print(f"   Answer length: {len(result['answer'])} chars")
        print(f"   Sources: {len(result['source_documents'])} documents")
    
    def test_specific_cuisine(self):
        """Test cuisine-specific query"""
        assert self.rag is not None, "RAG system not initialized"
        query = "Rajasthani food"
        result = self.rag.query(query)
        
        answer_lower = result["answer"].lower()
        
        # Should mention Rajasthani or related terms
        rajasthani_terms = ["rajasthani", "dal baati", "traditional"]
        has_relevant_term = any(term in answer_lower for term in rajasthani_terms)
        
        assert has_relevant_term, "Answer doesn't mention Rajasthani cuisine"
        
        print(f"   Found Rajasthani-related content: ✅")
    
    def test_price_query(self):
        """Test price-related query"""
        assert self.rag is not None, "RAG system not initialized"
        query = "budget friendly restaurants"
        result = self.rag.query(query)
        
        answer_lower = result["answer"].lower()
        
        # Should mention price or budget
        price_terms = ["₹", "budget", "affordable", "cheap", "inexpensive", "price"]
        has_price_mention = any(term in answer_lower for term in price_terms)
        
        assert has_price_mention, "Answer doesn't address budget/price"
        
        print(f"   Addresses price/budget: ✅")
    
    def test_dish_specific(self):
        """Test dish-specific query"""
        assert self.rag is not None, "RAG system not initialized"
        query = "where can I get dal baati churma"
        result = self.rag.query(query)
        
        answer_lower = result["answer"].lower()
        
        # Should mention the dish or related restaurants
        assert "dal baati" in answer_lower or "restaurant" in answer_lower
        
        print(f"   Mentions dal baati or restaurants: ✅")
    
    def test_response_time(self):
        """Test response time is acceptable"""
        assert self.rag is not None, "RAG system not initialized"
        query = "best restaurants"
        
        start = time.time()
        result = self.rag.query(query)
        elapsed = time.time() - start
        
        assert elapsed < 10, f"Response too slow: {elapsed:.2f}s"
        
        print(f"   Response time: {elapsed:.2f}s")
        
        if elapsed < 3:
            print(f"   Performance: Excellent ⚡")
        elif elapsed < 5:
            print(f"   Performance: Good ✅")
        else:
            print(f"   Performance: Acceptable ⏱️")
    
    def test_source_attribution(self):
        """Test that sources are properly attributed"""
        assert self.rag is not None, "RAG system not initialized"
        query = "vegetarian food"
        result = self.rag.query(query)
        
        sources = result["source_documents"]
        
        # Check sources have required metadata
        for source in sources:
            assert hasattr(source, 'metadata'), "Source missing metadata"
            assert 'restaurant' in source.metadata, "Source missing restaurant name"
            assert 'rating' in source.metadata, "Source missing rating"
        
        print(f"   All {len(sources)} sources have proper metadata: ✅")
    
    def test_empty_query_handling(self):
        """Test handling of empty query"""
        assert self.rag is not None, "RAG system not initialized"
        try:
            result = self.rag.query("")
            # Should either handle gracefully or raise appropriate error
            print(f"   Empty query handled gracefully: ✅")
        except Exception as e:
            print(f"   Empty query raises error (acceptable): {type(e).__name__}")
    
    def test_long_query_handling(self):
        """Test handling of very long query"""
        assert self.rag is not None, "RAG system not initialized"
        long_query = "I am looking for " + "very " * 50 + "good restaurants"
        result = self.rag.query(long_query)
        
        assert result is not None, "Failed on long query"
        assert len(result["answer"]) > 0, "No answer for long query"
        
        print(f"   Long query handled: ✅")
    
    def test_multiple_cuisine_query(self):
        """Test query with multiple cuisine types"""
        assert self.rag is not None, "RAG system not initialized"
        query = "Italian or Rajasthani restaurants"
        result = self.rag.query(query)
        
        answer_lower = result["answer"].lower()
        
        # Should mention at least one cuisine
        has_cuisine = "italian" in answer_lower or "rajasthani" in answer_lower
        
        assert has_cuisine, "Doesn't address multiple cuisines"
        
        print(f"   Handles multiple cuisines: ✅")
    
    def run_all_tests(self):
        """Run all tests"""
        
        # Setup
        if not self.setup():
            print("\n❌ Setup failed, cannot run tests")
            return
        
        # Run tests
        print("\n" + "="*60)
        print("RUNNING TEST SUITE")
        print("="*60)
        
        self.test_case("Basic Query", self.test_basic_query)
        self.test_case("Specific Cuisine", self.test_specific_cuisine)
        self.test_case("Price Query", self.test_price_query)
        self.test_case("Dish Specific", self.test_dish_specific)
        self.test_case("Response Time", self.test_response_time)
        self.test_case("Source Attribution", self.test_source_attribution)
        self.test_case("Empty Query Handling", self.test_empty_query_handling)
        self.test_case("Long Query Handling", self.test_long_query_handling)
        self.test_case("Multiple Cuisine Query", self.test_multiple_cuisine_query)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = self.test_results["total"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        print(f"\nPass Rate: {pass_rate:.1f}%")
        
        if pass_rate == 100:
            print("\n🎉 ALL TESTS PASSED! System is ready for deployment!")
        elif pass_rate >= 80:
            print("\n✅ Most tests passed. System is mostly ready.")
        else:
            print("\n⚠️  Several tests failed. Review issues before deploying.")
        
        print("="*60)


def main():
    tester = SystemTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
