"""
Exercise 5: Data Validation
Goal: Ensure scraped data meets quality standards
"""

import json
from datetime import datetime
import os


# ------------------ LOAD JSON DATA ------------------

JSON_PATH = "data/sample_template.json"   # 🔁 change if filename differs

try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ Loaded data from: {JSON_PATH}")
except FileNotFoundError:
    print(f"❌ File not found: {JSON_PATH}")
    print("👉 Check if your terminal is in project root and file exists.")
    exit()
except json.JSONDecodeError:
    print(f"❌ Invalid JSON format in: {JSON_PATH}")
    exit()


# ------------------ VALIDATION FUNCTION ------------------

def validate_restaurant_data(data):
    """
    Validate restaurant data structure and content
    """
    print("=" * 60)
    print("DATA VALIDATION REPORT")
    print("=" * 60)

    errors = []
    warnings = []
    stats = {
        "total_restaurants": 0,
        "total_reviews": 0,
        "avg_rating": 0,
        "missing_fields": []
    }

    # Required fields
    required_restaurant_fields = ["name", "cuisine", "rating", "reviews"]
    required_review_fields = ["text", "rating", "author", "date"]

    if "restaurants" not in data:
        errors.append("❌ Missing 'restaurants' key in data")
        return errors, warnings, stats

    restaurants = data["restaurants"]
    stats["total_restaurants"] = len(restaurants)

    ratings = []

    for i, restaurant in enumerate(restaurants):
        rest_name = restaurant.get("name", f"Restaurant #{i+1}")

        # Check required fields
        for field in required_restaurant_fields:
            if field not in restaurant:
                errors.append(f"❌ {rest_name}: Missing '{field}'")

        # Validate rating
        if "rating" in restaurant:
            rating = restaurant["rating"]
            if not isinstance(rating, (int, float)):
                errors.append(f"❌ {rest_name}: Invalid rating type")
            elif rating < 0 or rating > 5:
                errors.append(f"❌ {rest_name}: Rating out of range (0–5)")
            else:
                ratings.append(rating)

        # Validate reviews
        if "reviews" in restaurant:
            reviews = restaurant["reviews"]
            stats["total_reviews"] += len(reviews)

            if len(reviews) == 0:
                warnings.append(f"⚠️  {rest_name}: No reviews found")

            for j, review in enumerate(reviews):
                # Check required review fields
                for field in required_review_fields:
                    if field not in review:
                        errors.append(
                            f"❌ {rest_name}, Review #{j+1}: Missing '{field}'"
                        )

                # Validate review text length
                if "text" in review:
                    text_length = len(review["text"])
                    if text_length < 10:
                        warnings.append(
                            f"⚠️  {rest_name}, Review #{j+1}: "
                            f"Review too short ({text_length} chars)"
                        )
                    elif text_length > 1000:
                        warnings.append(
                            f"⚠️  {rest_name}, Review #{j+1}: "
                            f"Review very long ({text_length} chars)"
                        )

                # Validate date format
                if "date" in review:
                    try:
                        datetime.strptime(review["date"], "%Y-%m-%d")
                    except ValueError:
                        errors.append(
                            f"❌ {rest_name}, Review #{j+1}: "
                            f"Invalid date format (should be YYYY-MM-DD)"
                        )

    # Calculate average rating
    if ratings:
        stats["avg_rating"] = round(sum(ratings) / len(ratings), 2)

    return errors, warnings, stats


# ------------------ RUN VALIDATION ------------------

errors, warnings, stats = validate_restaurant_data(data)

print(f"\n📊 STATISTICS:")
print(f"   Total Restaurants: {stats['total_restaurants']}")
print(f"   Total Reviews: {stats['total_reviews']}")
print(f"   Average Rating: {stats['avg_rating']}")

if errors:
    print(f"\n❌ ERRORS FOUND ({len(errors)}):")
    for error in errors:
        print(f"   {error}")
else:
    print("\n✅ No errors found!")

if warnings:
    print(f"\n⚠️  WARNINGS ({len(warnings)}):")
    for warning in warnings:
        print(f"   {warning}")
else:
    print("\n✅ No warnings!")

print("\n" + "=" * 60)
if not errors:
    print("✅ DATA VALIDATION PASSED!")
else:
    print("❌ DATA VALIDATION FAILED - Fix errors above")
print("=" * 60)





