"""
Main scraper logic
Handles fetching pages and coordinating extraction
"""

import time
import random
import requests
from pathlib import Path
from src.scraper.config import SETTINGS, HEADERS
from src.scraper.extractors import extract_restaurant_data
from src.scraper.utils import print_progress, validate_url


def fetch_page(url):
    """
    Fetch HTML content from URL or file
    
    Args:
        url: URL string or file path
    
    Returns:
        HTML content as string, or None if error
    """
    try:
        # Check if it's a local file
        if url.endswith('.html') and Path(url).exists():
            with open(url, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Otherwise, fetch from web
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=SETTINGS['timeout']
        )
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"  ❌ Status code: {response.status_code}")
            return None
    
    except requests.Timeout:
        print(f"  ❌ Timeout after {SETTINGS['timeout']}s")
        return None
    except requests.RequestException as e:
        print(f"  ❌ Request error: {e}")
        return None
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return None


def scrape_restaurant(url, index=0, total=1):
    """
    Scrape a single restaurant
    
    Args:
        url: URL or file path to scrape
        index: Current index (for progress tracking)
        total: Total number of URLs (for progress tracking)
    
    Returns:
        Restaurant data dictionary or None if error
    """
    print(f"\n[{index+1}/{total}] Scraping: {url}")
    
    # Validate URL
    if not validate_url(url):
        print(f"  ❌ Invalid URL: {url}")
        return None
    
    # Fetch page
    html_content = fetch_page(url)
    if not html_content:
        return None
    
    print(f"  ✅ Page fetched successfully")
    
    # Extract data
    try:
        restaurant_data = extract_restaurant_data(html_content)
        
        # Log what we found
        name = restaurant_data.get("name", "Unknown")
        rating = restaurant_data.get("rating", 0)
        review_count = len(restaurant_data.get("reviews", []))
        
        print(f"  ✅ {name} | Rating: {rating}⭐ | Reviews: {review_count}")
        
        return restaurant_data
    
    except Exception as e:
        print(f"  ❌ Extraction error: {e}")
        return None


def scrape_multiple(urls):
    """
    Scrape multiple restaurants with rate limiting
    
    Args:
        urls: List of URLs to scrape
    
    Returns:
        List of restaurant data dictionaries
    """
    results = []
    total = len(urls)
    
    print("="*60)
    print(f"Starting scrape of {total} restaurants")
    print("="*60)
    
    for i, url in enumerate(urls):
        # Scrape
        data = scrape_restaurant(url, i, total)
        
        if data:
            results.append(data)
        
        # Rate limiting (except for last item)
        if i < total - 1:
            delay = random.uniform(
                SETTINGS['delay_min'],
                SETTINGS['delay_max']
            )
            print(f"  ⏱️  Waiting {delay:.1f}s before next request...")
            time.sleep(delay)
    
    print("\n" + "="*60)
    print(f"✅ Scraping complete! Collected {len(results)}/{total} restaurants")
    print("="*60)
    
    return results
