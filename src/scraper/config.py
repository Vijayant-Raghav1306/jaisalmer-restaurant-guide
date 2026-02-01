"""
Configuration file for the scraper
Contains URLs, selectors, and settings
"""

# Scraping settings
SETTINGS = {
    "delay_min": 2,        # Minimum seconds between requests
    "delay_max": 4,        # Maximum seconds between requests
    "timeout": 10,         # Request timeout in seconds
    "max_retries": 3,      # Retry failed requests
    "save_checkpoint": 5,  # Save after every N restaurants
}

# Request headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'JaisalmerRestaurantBot/1.0 (Educational Project)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

# For testing: We'll create simple test pages
# These will be local HTML files we control
TEST_URLS = [
    "test_data/trio_restaurant.html",
    "test_data/jaisal_italy.html",
    "test_data/saffron_cafe.html",
]

# Real URLs (to be populated after testing)
# For now, we'll use publicly accessible review sites
REAL_URLS = [
    # TODO: Add actual restaurant URLs after testing
    # Example format:
    # "https://example-review-site.com/jaisalmer/trio-restaurant",
]

# CSS Selectors (will vary by website)
# These are examples - adjust based on actual HTML structure
SELECTORS = {
    "restaurant_name": "h1.restaurant-name",
    "rating": "span.rating-number",
    "cuisine": "span.cuisine-type",
    "price_range": "span.price-range",
    "review_container": "div.review-card",
    "review_text": "p.review-text",
    "review_author": "span.author-name",
    "review_date": "span.review-date",
    "review_rating": "span.review-rating",
}

# Output paths
OUTPUT_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
CHECKPOINT_FILE = "data/raw/checkpoint.json"
