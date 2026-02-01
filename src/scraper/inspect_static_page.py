"""
Exercise 2: Practice scraping on a simple static page
Goal: Understand BeautifulSoup basics
"""

import requests
from bs4 import BeautifulSoup

print("="*60)
print("EXERCISE 2: Inspecting Static HTML")
print("="*60)

# We'll use a simple example HTML
example_html = """
<html>
  <body>
    <div class="restaurant-card">
      <h2 class="name">Trio Restaurant</h2>
      <div class="rating-box">
        <span class="stars">★★★★☆</span>
        <span class="number">4.5</span>
      </div>
      <p class="cuisine">Rajasthani, North Indian</p>
      <span class="price">₹₹</span>
      
      <div class="review">
        <p class="text">Amazing dal baati churma! Authentic flavors.</p>
        <span class="author">Vikas S.</span>
        <span class="date">2025-01-20</span>
      </div>
      
      <div class="review">
        <p class="text">Great rooftop view of the fort. Must visit!</p>
        <span class="author">Priya M.</span>
        <span class="date">2025-01-15</span>
      </div>
    </div>
  </body>
</html>
"""

# Parse the HTML
soup = BeautifulSoup(example_html, 'html.parser')

print("\n📄 Sample HTML loaded")
print("\n" + "="*60)
print("EXTRACTION PRACTICE")
print("="*60)

# Extract restaurant name
print("\n1️⃣  Extracting Restaurant Name:")
print("   Code: soup.find('h2', class_='name').text")
name = soup.find('h2', class_='name').text
print(f"   Result: '{name}'")

# Extract rating
print("\n2️⃣  Extracting Rating:")
print("   Code: soup.find('span', class_='number').text")
rating = soup.find('span', class_='number').text
print(f"   Result: '{rating}'")

# Extract cuisine
print("\n3️⃣  Extracting Cuisine:")
print("   Code: soup.find('p', class_='cuisine').text")
cuisine = soup.find('p', class_='cuisine').text
print(f"   Result: '{cuisine}'")

# Extract all reviews
print("\n4️⃣  Extracting All Reviews:")
print("   Code: soup.find_all('div', class_='review')")
reviews = soup.find_all('div', class_='review')
print(f"   Found: {len(reviews)} reviews\n")

for i, review in enumerate(reviews, 1):
    text = review.find('p', class_='text').text
    author = review.find('span', class_='author').text
    date = review.find('span', class_='date').text
    
    print(f"   Review {i}:")
    print(f"   Text: {text}")
    print(f"   Author: {author}")
    print(f"   Date: {date}")
    print()

# Create structured data
print("="*60)
print("CREATING STRUCTURED DATA")
print("="*60)

restaurant_data = {
    "name": name,
    "rating": float(rating),
    "cuisine": cuisine,
    "price_range": soup.find('span', class_='price').text,
    "reviews": []
}

for review in reviews:
    review_data = {
        "text": review.find('p', class_='text').text,
        "author": review.find('span', class_='author').text,
        "date": review.find('span', class_='date').text
    }
    restaurant_data["reviews"].append(review_data)

import json
print("\n📦 Structured JSON output:")
print(json.dumps(restaurant_data, indent=2, ensure_ascii=False))

print("\n" + "="*60)
print("✅ EXERCISE COMPLETE!")
print("="*60)
print("\nYou've learned:")
print("• How to parse HTML with BeautifulSoup")
print("• How to extract data using CSS selectors")
print("• How to structure extracted data as JSON")
print("• This is EXACTLY what we'll do with real websites!")
print("="*60)
