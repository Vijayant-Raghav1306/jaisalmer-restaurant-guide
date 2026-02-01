"""
Blog Scraper v2
Scrapes restaurant reviews from blog posts and articles
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from src.scraper.utils import save_json, clean_text


class BlogScraper:
    """Extract restaurant reviews from blog posts"""
    
    def __init__(self, restaurant_list_file=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/91.0.4472.124 Safari/537.36'
        }
        self.restaurant_names = []
        
        # Load restaurant names if provided
        if restaurant_list_file:
            self.load_restaurant_names(restaurant_list_file)
    
    def load_restaurant_names(self, filepath):
        """Load restaurant names from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    # Extract just the name (before |)
                    name = line.split('|')[0].strip()
                    self.restaurant_names.append(name.lower())
            
            print(f"📋 Loaded {len(self.restaurant_names)} restaurant names")
        except Exception as e:
            print(f"⚠️  Could not load restaurant list: {e}")
    
    def fetch_page(self, url):
        """Fetch webpage content"""
        try:
            print(f"\n🔍 Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                print(f"  ✅ Success ({len(response.text)} bytes)")
                return response.text
            else:
                print(f"  ❌ Failed with status {response.status_code}")
                return None
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def extract_main_content(self, html):
        """Extract main article content from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 
                            'header', 'aside', 'iframe']):
            element.decompose()
        
        # Try common content containers
        content = None
        selectors = [
            'article',
            '.post-content',
            '.entry-content',
            '.article-content',
            'main',
            '.content',
            '#content',
            '.post',
            '.blog-post'
        ]
        
        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                print(f"  ✅ Found content using selector: {selector}")
                break
        
        if not content:
            # Fallback to body
            content = soup.find('body')
            print(f"  ⚠️  Using fallback (body tag)")
        
        return content
    
    def extract_paragraphs(self, content):
        """Extract paragraphs from content"""
        if not content:
            return []
        
        # Get all paragraphs
        paragraphs = content.find_all('p')
        
        # Clean and filter
        cleaned = []
        for p in paragraphs:
            text = clean_text(p.get_text())
            # Only keep substantial paragraphs
            if len(text) > 50:  # At least 50 characters
                cleaned.append(text)
        
        print(f"  ✅ Extracted {len(cleaned)} paragraphs")
        return cleaned
    
    def find_restaurant_mentions(self, text):
        """
        Find restaurant names mentioned in text
        Returns list of matched restaurant names
        """
        found = []
        text_lower = text.lower()
        
        for name in self.restaurant_names:
            if name in text_lower:
                # Get the original case from text
                found.append(name.title())
        
        return found
    
    def extract_reviews(self, paragraphs, source_url):
        """Extract restaurant reviews from paragraphs"""
        reviews = []
        
        # Keywords that indicate a review/recommendation
        review_keywords = [
            'restaurant', 'food', 'dish', 'menu', 'delicious',
            'tasty', 'authentic', 'recommend', 'must try',
            'best', 'excellent', 'amazing', 'great', 'good',
            'try', 'visit', 'eat', 'dining', 'cafe'
        ]
        
        for para in paragraphs:
            para_lower = para.lower()
            
            # Check if paragraph talks about restaurants/food
            keyword_count = sum(1 for kw in review_keywords if kw in para_lower)
            
            if keyword_count >= 2:  # At least 2 food-related keywords
                # Try to find restaurant names
                restaurants = self.find_restaurant_mentions(para)
                
                review = {
                    "text": para,
                    "author": "Travel Blogger",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": source_url,
                    "source_type": "blog",
                    "rating": 0  # We don't know rating from blogs
                }
                
                if restaurants:
                    # If we found restaurant names, create separate reviews
                    for rest_name in restaurants:
                        review_copy = review.copy()
                        review_copy["restaurant_name"] = rest_name
                        reviews.append(review_copy)
                else:
                    # Generic review about Jaisalmer food
                    review["restaurant_name"] = "General"
                    reviews.append(review)
        
        return reviews
    
    def scrape_url(self, url):
        """Scrape a single URL"""
        # Fetch page
        html = self.fetch_page(url)
        if not html:
            return []
        
        # Extract content
        content = self.extract_main_content(html)
        if not content:
            print("  ⚠️  No content found")
            return []
        
        # Extract paragraphs
        paragraphs = self.extract_paragraphs(content)
        if not paragraphs:
            print("  ⚠️  No paragraphs found")
            return []
        
        # Extract reviews
        reviews = self.extract_reviews(paragraphs, url)
        print(f"  ✅ Extracted {len(reviews)} review snippets")
        
        return reviews
    
    def scrape_multiple(self, urls):
        """Scrape multiple URLs"""
        print("="*60)
        print("BLOG SCRAPER - MULTIPLE URLS")
        print("="*60)
        
        all_reviews = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}]")
            reviews = self.scrape_url(url)
            all_reviews.extend(reviews)
            
            # Be respectful - wait between requests
            if i < len(urls):
                wait_time = 2
                print(f"  ⏱️  Waiting {wait_time}s before next request...")
                time.sleep(wait_time)
        
        print("\n" + "="*60)
        print(f"✅ Total reviews collected: {len(all_reviews)}")
        print("="*60)
        
        return all_reviews


def main():
    """Main function with example usage"""
    
    print("="*60)
    print("BLOG SCRAPER")
    print("="*60)
    
    print("\n📋 INSTRUCTIONS:")
    print("1. Find 3-5 blog posts about Jaisalmer restaurants")
    print("2. Add URLs to the 'blog_urls' list below")
    print("3. Run this script")
    print("="*60)
    
    # YOUR BLOG URLs HERE
    # Search Google for: "best restaurants jaisalmer blog"
    # Add the URLs you find
    blog_urls = [
        # Example (replace with real URLs you find):
        "https://www.wannabemaven.com/rajasthani-food-in-jaisalmer/?utm_source=chatgpt.com",
        "https://www.travellingcamera.com/2023/01/rooftop-restaurants-inside-jaisalmer.html?utm_source=chatgpt.com",
        "https://www.wannabemaven.com/rajasthani-food-in-jaisalmer/?utm_source=chatgpt.com",
    ]
    
    if not blog_urls:
        print("\n⚠️  No URLs provided!")
        print("   Please add blog URLs to the 'blog_urls' list in this script")
        print("\n💡 How to find URLs:")
        print("   1. Google: 'best restaurants jaisalmer blog 2024'")
        print("   2. Look for blog posts (not TripAdvisor/Google)")
        print("   3. Copy the URL")
        print("   4. Add to the list above")
        return
    
    # Create scraper
    scraper = BlogScraper(restaurant_list_file="data/restaurant_list.txt")
    
    # Scrape URLs
    reviews = scraper.scrape_multiple(blog_urls)
    
    if not reviews:
        print("\n⚠️  No reviews extracted")
        print("   The blogs might not mention specific restaurants")
        print("   Or the HTML structure is complex")
        return
    
    # Organize by restaurant
    by_restaurant = {}
    for review in reviews:
        rest_name = review.get("restaurant_name", "General")
        if rest_name not in by_restaurant:
            by_restaurant[rest_name] = []
        by_restaurant[rest_name].append(review)
    
    # Create output
    output = {
        "metadata": {
            "source": "blog_scraping",
            "collection_date": datetime.now().strftime("%Y-%m-%d"),
            "urls_scraped": len(blog_urls),
            "total_reviews": len(reviews),
            "restaurants_found": len(by_restaurant)
        },
        "restaurants": []
    }
    
    # Format as restaurant objects
    for rest_name, rest_reviews in by_restaurant.items():
        restaurant = {
            "name": rest_name,
            "rating": 0,
            "cuisine": [],
            "reviews": rest_reviews,
            "source": "blog_scraping"
        }
        output["restaurants"].append(restaurant)
    
    # Save
    output_file = "data/raw/blog_reviews.json"
    save_json(output, output_file)
    
    # Report
    print(f"\n📄 Summary:")
    print(f"   URLs scraped: {len(blog_urls)}")
    print(f"   Total reviews: {len(reviews)}")
    print(f"   Restaurants mentioned: {len(by_restaurant)}")
    print(f"   Saved to: {output_file}")
    
    print("\n🏆 Top mentioned restaurants:")
    sorted_rests = sorted(by_restaurant.items(), 
                         key=lambda x: len(x[1]), 
                         reverse=True)
    for rest_name, rest_reviews in sorted_rests[:5]:
        print(f"   {rest_name}: {len(rest_reviews)} mentions")


if __name__ == "__main__":
    main()
