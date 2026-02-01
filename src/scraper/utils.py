"""
Utility functions for scraping
"""

import json
import os
from datetime import datetime
from pathlib import Path


def ensure_dirs():
    """Create necessary directories if they don't exist"""
    dirs = ['data/raw', 'data/processed', 'test_data']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Directories verified")


def save_json(data, filepath):
    """
    Save data to JSON file
    
    Args:
        data: Python dict or list to save
        filepath: Path to save file
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved to: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving {filepath}: {e}")
        return False


def load_json(filepath):
    """
    Load data from JSON file
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Loaded data or None if error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded from: {filepath}")
        return data
    except FileNotFoundError:
        print(f"⚠️  File not found: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in: {filepath}")
        return None


def clean_text(text):
    """
    Clean extracted text
    
    Args:
        text: Raw text string
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters (optional - be careful!)
    # text = text.replace('\n', ' ').replace('\r', '')
    
    return text.strip()


def generate_id(prefix, index):
    """
    Generate unique ID
    
    Args:
        prefix: ID prefix (e.g., 'rest', 'rev')
        index: Numeric index
    
    Returns:
        Formatted ID (e.g., 'rest_001')
    """
    return f"{prefix}_{str(index).zfill(3)}"


def create_metadata():
    """
    Create metadata for the dataset
    
    Returns:
        Metadata dictionary
    """
    return {
        "source": "web_scraping",
        "city": "Jaisalmer",
        "country": "India",
        "collection_date": datetime.now().strftime("%Y-%m-%d"),
        "scraper_version": "1.0",
    }


def print_progress(current, total, item_name=""):
    """
    Print progress indicator
    
    Args:
        current: Current item number
        total: Total items
        item_name: Optional name of current item
    """
    percentage = (current / total) * 100
    bar_length = 30
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    print(f"\r[{current}/{total}] {bar} {percentage:.1f}% | {item_name}", 
          end='', flush=True)
    
    if current == total:
        print()  # New line when complete


def validate_url(url):
    """
    Basic URL validation
    
    Args:
        url: URL string to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not url:
        return False
    
    # Check if it's a file path (for testing)
    if url.endswith('.html'):
        return os.path.exists(url)
    
    # Check if it's a web URL
    return url.startswith('http://') or url.startswith('https://')


# For testing - create a simple report
def generate_report(data):
    """
    Generate a summary report of scraped data
    
    Args:
        data: Scraped data dictionary
    
    Returns:
        Report string
    """
    report = []
    report.append("="*60)
    report.append("SCRAPING REPORT")
    report.append("="*60)
    
    if "metadata" in data:
        report.append(f"\nCollection Date: {data['metadata'].get('collection_date', 'N/A')}")
        report.append(f"City: {data['metadata'].get('city', 'N/A')}")
    
    if "restaurants" in data:
        restaurants = data["restaurants"]
        total_reviews = sum(len(r.get("reviews", [])) for r in restaurants)
        avg_rating = sum(r.get("rating", 0) for r in restaurants) / len(restaurants) if restaurants else 0
        
        report.append(f"\nTotal Restaurants: {len(restaurants)}")
        report.append(f"Total Reviews: {total_reviews}")
        report.append(f"Average Rating: {avg_rating:.2f}")
        
        report.append("\n" + "-"*60)
        report.append("Restaurant Summary:")
        report.append("-"*60)
        
        for rest in restaurants:
            name = rest.get("name", "Unknown")
            rating = rest.get("rating", 0)
            review_count = len(rest.get("reviews", []))
            report.append(f"  • {name}: {rating}⭐ ({review_count} reviews)")
    
    report.append("="*60)
    
    return "\n".join(report)
