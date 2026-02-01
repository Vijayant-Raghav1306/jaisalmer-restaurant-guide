"""
Main runner script for the scraper
This is what you execute to start scraping
"""

import sys
from pathlib import Path

# Add src to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scraper.config import TEST_URLS
from src.scraper.scraper import scrape_multiple
from src.scraper.utils import (
    ensure_dirs, 
    save_json, 
    create_metadata,
    generate_report
)


def main():
    """
    Main function - orchestrates the entire scraping process
    """
    print("="*60)
    print("JAISALMER RESTAURANT SCRAPER v1.0")
    print("="*60)
    
    # Step 1: Setup
    print("\n📁 Setting up directories...")
    ensure_dirs()
    
    # Step 2: Get URLs to scrape
    urls = TEST_URLS  # Using test files for now
    print(f"\n📋 Found {len(urls)} URLs to scrape")
    for i, url in enumerate(urls, 1):
        print(f"   {i}. {url}")
    
    # Step 3: Confirm before proceeding
    print("\n" + "="*60)
    response = input("Continue with scraping? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Scraping cancelled")
        return
    
    # Step 4: Scrape!
    print("\n🚀 Starting scraping process...\n")
    restaurants = scrape_multiple(urls)
    
    # Step 5: Structure the data
    print("\n📦 Structuring data...")
    final_data = {
        "metadata": create_metadata(),
        "restaurants": restaurants
    }
    
    # Update metadata with counts
    final_data["metadata"]["total_restaurants"] = len(restaurants)
    final_data["metadata"]["total_reviews"] = sum(
        len(r.get("reviews", [])) for r in restaurants
    )
    
    # Step 6: Save to file
    output_file = "data/raw/scraped_restaurants.json"
    print(f"\n💾 Saving to {output_file}...")
    save_json(final_data, output_file)
    
    # Step 7: Generate and display report
    print("\n" + generate_report(final_data))
    
    print("\n✅ All done! Check the output file:")
    print(f"   {output_file}")
    print("="*60)


if __name__ == "__main__":
    main()
