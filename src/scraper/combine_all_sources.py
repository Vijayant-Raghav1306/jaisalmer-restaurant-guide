"""
Combine All Data Sources
Merges blog scraping, manual entry, and Zomato data
"""

import json
from pathlib import Path
from datetime import datetime
from src.scraper.utils import save_json, load_json


class DataCombiner:
    """Combine data from multiple sources"""

    def __init__(self):
        self.sources = {
            "blog_scraping": "data/raw/blog_reviews.json",
            "manual_collection": "data/raw/manual_collection.json",
            "zomato_dataset": "data/raw/zomato_adapted.json"
        }
        self.all_restaurants = []

    def load_all_sources(self):
        """Load data from all available sources"""
        print("=" * 60)
        print("LOADING DATA FROM ALL SOURCES")
        print("=" * 60)

        loaded = {}

        for source_name, filepath in self.sources.items():
            data = load_json(filepath)
            if data:
                restaurants = data.get("restaurants", [])
                loaded[source_name] = restaurants
                print(f"✅ {source_name}: {len(restaurants)} restaurants")
            else:
                print(f"⚠️  {source_name}: Not found")
                loaded[source_name] = []

        return loaded

    def merge_restaurants(self, loaded_data):
        """
        Merge restaurants from all sources
        Combines reviews for same restaurant
        """
        print("\n" + "=" * 60)
        print("MERGING RESTAURANTS")
        print("=" * 60)

        # Dictionary to hold unique restaurants
        restaurant_dict = {}

        for source_name, restaurants in loaded_data.items():
            print(f"\n📝 Processing {source_name}...")

            for rest in restaurants:
                name = rest.get("name", "Unknown")

                # Normalize name (lowercase, remove extra spaces)
                name_key = " ".join(name.lower().split())

                if name_key in restaurant_dict:
                    # Restaurant exists - merge reviews
                    existing = restaurant_dict[name_key]
                    new_reviews = rest.get("reviews", [])
                    existing["reviews"].extend(new_reviews)

                    # Update rating if better
                    if rest.get("rating", 0) > existing.get("rating", 0):
                        existing["rating"] = rest.get("rating", 0)

                    # Merge cuisines
                    new_cuisines = rest.get("cuisine", [])
                    for cuisine in new_cuisines:
                        if cuisine and cuisine not in existing.get("cuisine", []):
                            existing["cuisine"].append(cuisine)

                    print(f"  🔄 Merged: {name} (+{len(new_reviews)} reviews)")
                else:
                    # New restaurant
                    restaurant_dict[name_key] = {
                        "name": name,  # Keep original case
                        "rating": rest.get("rating", 0),
                        "cuisine": rest.get("cuisine", []),
                        "price_range": rest.get("price_range", "₹₹"),
                        "address": rest.get("address", ""),
                        "phone": rest.get("phone", ""),
                        "reviews": rest.get("reviews", []),
                        "sources": [source_name]
                    }
                    print(f"  ➕ Added: {name}")

        return list(restaurant_dict.values())

    def clean_and_validate(self, restaurants):
        """Clean and validate the merged data"""
        print("\n" + "=" * 60)
        print("CLEANING AND VALIDATING")
        print("=" * 60)

        cleaned = []

        for rest in restaurants:
            # Remove duplicates in reviews
            unique_reviews = []
            seen_texts = set()

            for review in rest.get("reviews", []):
                text = review.get("text", "")
                # Use first 50 chars as uniqueness key
                text_key = text[:50].lower().strip()

                if text_key and text_key not in seen_texts and len(text) > 20:
                    seen_texts.add(text_key)
                    unique_reviews.append(review)

            rest["reviews"] = unique_reviews

            # Only keep restaurants with at least 1 review
            if len(unique_reviews) > 0:
                cleaned.append(rest)
                print(f"  ✅ {rest['name']}: {len(unique_reviews)} reviews")
            else:
                print(f"  ❌ Skipped {rest['name']}: No reviews")

        return cleaned

    def generate_statistics(self, restaurants):
        """Generate dataset statistics"""
        total_reviews = sum(len(r["reviews"]) for r in restaurants)
        avg_reviews = total_reviews / len(restaurants) if restaurants else 0
        avg_rating = (
            sum(r.get("rating", 0) for r in restaurants) / len(restaurants)
            if restaurants else 0
        )

        # Count by source
        source_counts = {}
        for rest in restaurants:
            for source in rest.get("sources", ["unknown"]):
                source_counts[source] = source_counts.get(source, 0) + 1

        stats = {
            "total_restaurants": len(restaurants),
            "total_reviews": total_reviews,
            "avg_reviews_per_restaurant": round(avg_reviews, 2),
            "avg_rating": round(avg_rating, 2),
            "source_distribution": source_counts
        }

        return stats

    def combine(self):
        """Main combination process"""
        print("=" * 60)
        print("DATA COMBINER - ALL SOURCES")
        print("=" * 60)

        # Load all sources
        loaded_data = self.load_all_sources()

        if not any(loaded_data.values()):
            print("\n❌ No data found from any source!")
            print("\nMake sure you've run:")
            print("1. python src/scraper/blog_scraper_v2.py")
            print("2. python src/scraper/quick_collector_v2.py")
            print("3. python src/scraper/zomato_adapter.py")
            return None

        # Merge restaurants
        merged = self.merge_restaurants(loaded_data)

        # Clean and validate
        cleaned = self.clean_and_validate(merged)

        if not cleaned:
            print("\n❌ No valid restaurants after cleaning")
            return None

        # Generate statistics
        stats = self.generate_statistics(cleaned)

        # Create final output
        output = {
            "metadata": {
                "source": "combined_all_sources",
                "collection_date": datetime.now().strftime("%Y-%m-%d"),
                "version": "1.0",
                **stats
            },
            "restaurants": cleaned
        }

        return output


def main():
    """Main execution"""

    combiner = DataCombiner()
    output = combiner.combine()

    if output:
        # Save final dataset
        final_file = "data/processed/final_dataset.json"
        save_json(output, final_file)

        # Print final report
        print("\n" + "=" * 60)
        print("🎉 FINAL DATASET CREATED!")
        print("=" * 60)

        metadata = output["metadata"]
        print(f"\n📊 STATISTICS:")
        print(f"   Total Restaurants: {metadata['total_restaurants']}")
        print(f"   Total Reviews: {metadata['total_reviews']}")
        print(f"   Avg Reviews/Restaurant: {metadata['avg_reviews_per_restaurant']}")
        print(f"   Average Rating: {metadata['avg_rating']}⭐")

        print(f"\n📁 Source Distribution:")
        for source, count in metadata["source_distribution"].items():
            print(f"   {source}: {count} restaurants")

        print(f"\n💾 Saved to: {final_file}")

        print("\n🏆 Top 10 Restaurants by Review Count:")
        sorted_rests = sorted(
            output["restaurants"],
            key=lambda x: len(x["reviews"]),
            reverse=True
        )

        for i, rest in enumerate(sorted_rests[:10], 1):
            print(f"   {i:2d}. {rest['name']}: {len(rest['reviews'])} reviews")

        print("\n" + "=" * 60)
        print("✅ READY FOR RAG SYSTEM!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. ✅ Data collection complete")
        print("2. ⏭️  Move to Ticket #6: Embeddings & ChromaDB")
        print("3. ⏭️  Then Ticket #7: Build RAG pipeline")
        print("=" * 60)
    else:
        print("\n❌ Failed to create final dataset")


if __name__ == "__main__":
    main()
