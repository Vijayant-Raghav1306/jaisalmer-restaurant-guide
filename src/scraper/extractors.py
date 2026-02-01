"""
Data extraction functions
Handles parsing HTML and extracting specific fields
"""

from bs4 import BeautifulSoup
from src.scraper.utils import clean_text
from src.scraper.config import SELECTORS


def extract_restaurant_name(soup):
    """Extract restaurant name from parsed HTML"""
    try:
        element = soup.find("h1", class_="restaurant-name")
        if element:
            return clean_text(element.text)
    except:
        pass
    return "Unknown Restaurant"


def extract_rating(soup):
    """Extract overall rating"""
    try:
        element = soup.find("span", class_="rating-number")
        if element:
            rating_text = clean_text(element.text)
            return float(rating_text)
    except:
        pass
    return 0.0


def extract_cuisine(soup):
    """Extract cuisine type"""
    try:
        element = soup.find("span", class_="cuisine-type")
        if element:
            return clean_text(element.text)
    except:
        pass
    return "Not specified"


def extract_price_range(soup):
    """Extract price range indicator"""
    try:
        element = soup.find("span", class_="price-range")
        if element:
            return clean_text(element.text)
    except:
        pass
    return "₹₹"


def extract_reviews(soup):
    """
    Extract all reviews from the page
    
    Returns:
        List of review dictionaries
    """
    reviews = []
    
    try:
        review_cards = soup.find_all("div", class_="review-card")
        
        for card in review_cards:
            review = {}
            
            # Extract review text
            text_elem = card.find("p", class_="review-text")
            review["text"] = clean_text(text_elem.text) if text_elem else ""
            
            # Extract rating
            rating_elem = card.find("span", class_="review-rating")
            try:
                review["rating"] = int(rating_elem.text) if rating_elem else 0
            except:
                review["rating"] = 0
            
            # Extract author
            author_elem = card.find("span", class_="author-name")
            review["author"] = clean_text(author_elem.text) if author_elem else "Anonymous"
            
            # Extract date
            date_elem = card.find("span", class_="review-date")
            review["date"] = clean_text(date_elem.text) if date_elem else ""
            
            # Only add if review text exists
            if review["text"]:
                reviews.append(review)
    
    except Exception as e:
        print(f"  ⚠️  Error extracting reviews: {e}")
    
    return reviews


def extract_restaurant_data(html_content):
    """
    Main extraction function - coordinates all extractions
    
    Args:
        html_content: Raw HTML string
    
    Returns:
        Dictionary with all restaurant data
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    restaurant_data = {
        "name": extract_restaurant_name(soup),
        "rating": extract_rating(soup),
        "cuisine": extract_cuisine(soup),
        "price_range": extract_price_range(soup),
        "reviews": extract_reviews(soup),
    }
    
    return restaurant_data
