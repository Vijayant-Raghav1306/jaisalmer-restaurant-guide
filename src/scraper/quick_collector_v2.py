"""
Quick Collector v2
Streamlined manual data entry with your restaurant list
"""

import json
from datetime import datetime
from pathlib import Path
from src.scraper.utils import save_json, ensure_dirs


class QuickCollector:
    """Fast manual data collection"""
    
    def __init__(self, restaurant_list_file):
        self.output_file = "data/raw/manual_collection.json"
        self.restaurant_list = []
        self.data = {
            "metadata": {
                "source": "manual_collection",
                "city": "Jaisalmer",
                "country": "India",
                "collection_date": datetime.now().strftime("%Y-%m-%d")
            },
            "restaurants": []
        }
        ensure_dirs()
        
        # Load existing data if available
        if Path(self.output_file).exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print(f"📂 Loaded existing data: {len(self.data['restaurants'])} restaurants")
            except:
                print("⚠️  Could not load existing file, starting fresh")
        
        # Load restaurant list
        self.load_restaurant_list(restaurant_list_file)
    
    def load_restaurant_list(self, filepath):
        """Load restaurant names from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse format: Name | Cuisine | Price
                    parts = [p.strip() for p in line.split('|')]
                    
                    restaurant = {
                        "name": parts[0] if len(parts) > 0 else line,
                        "cuisine": parts[1].split(',') if len(parts) > 1 else [],
                        "price_range": parts[2] if len(parts) > 2 else "₹₹"
                    }
                    
                    # Clean cuisine list
                    restaurant["cuisine"] = [c.strip() for c in restaurant["cuisine"]]
                    
                    self.restaurant_list.append(restaurant)
            
            print(f"📋 Loaded {len(self.restaurant_list)} restaurants from list")
        except Exception as e:
            print(f"❌ Error loading restaurant list: {e}")
    
    def show_menu(self):
        """Show restaurant selection menu"""
        print("\n" + "="*60)
        print("SELECT RESTAURANT")
        print("="*60)
        
        # Show already collected
        collected_names = [r["name"] for r in self.data["restaurants"]]
        
        print("\n📊 Progress:")
        print(f"   Collected: {len(collected_names)} restaurants")
        print(f"   Remaining: {len(self.restaurant_list) - len(collected_names)}")
        
        print("\n🍽️  Available restaurants:")
        print("-"*60)
        
        available = []
        for i, rest in enumerate(self.restaurant_list, 1):
            name = rest["name"]
            status = "✅" if name in collected_names else "  "
            available.append((i, name, status))
            print(f"{status} {i:2d}. {name}")
        
        print(f"\n   {len(self.restaurant_list) + 1}. Enter custom restaurant")
        print("   0. Save and exit")
        
        return available
    
    def quick_add_reviews(self, restaurant_info):
        """Quick review addition with paste support"""
        print("\n" + "="*60)
        print(f"📝 ADDING REVIEWS: {restaurant_info['name']}")
        print("="*60)
        
        restaurant = {
            "name": restaurant_info["name"],
            "rating": 0,
            "cuisine": restaurant_info.get("cuisine", []),
            "price_range": restaurant_info.get("price_range", "₹₹"),
            "reviews": [],
            "source": "manual"
        }
        
        # Quick rating
        rating_input = input(f"\nOverall rating (0-5) [skip]: ").strip()
        if rating_input:
            try:
                restaurant["rating"] = float(rating_input)
            except:
                restaurant["rating"] = 0
        
        # Add reviews
        print("\n" + "-"*60)
        print("ADD REVIEWS")
        print("-"*60)
        print("💡 TIP: Copy reviews from Google Maps and paste here!")
        print("   Add 2-3 reviews per restaurant for best results")
        print("-"*60)
        
        review_num = 1
        while review_num <= 5:  # Max 5 reviews per restaurant
            print(f"\n--- Review #{review_num} ---")
            
            choice = input("Add review? (y/n/done): ").lower()
            if choice in ['n', 'done', 'exit', 'q']:
                break
            
            if choice != 'y':
                print("Please enter 'y' to add or 'done' to finish")
                continue
            
            # Review text (multi-line support)
            print("\nPaste review text (press Enter twice when done):")
            lines = []
            empty_count = 0
            
            while empty_count < 2:
                try:
                    line = input()
                    if line.strip():
                        lines.append(line)
                        empty_count = 0
                    else:
                        empty_count += 1
                except EOFError:
                    break
            
            review_text = " ".join(lines).strip()
            
            if not review_text or len(review_text) < 20:
                print("⚠️  Review too short or empty, skipping...")
                continue
            
            # Quick metadata
            rating = input("Rating (1-5) [5]: ").strip()
            author = input("Author name [Anonymous]: ").strip()
            date = input("Date (YYYY-MM-DD) [today]: ").strip()
            
            review = {
                "text": review_text,
                "rating": int(rating) if rating and rating.isdigit() else 5,
                "author": author if author else "Anonymous",
                "date": date if date else datetime.now().strftime("%Y-%m-%d"),
                "source": "manual"
            }
            
            restaurant["reviews"].append(review)
            print(f"✅ Review {review_num} added ({len(review_text)} chars)")
            review_num += 1
        
        if not restaurant["reviews"]:
            print("\n⚠️  No reviews added for this restaurant")
            add_anyway = input("Save restaurant anyway? (y/n): ").lower()
            if add_anyway != 'y':
                return None
        
        print(f"\n✅ Added {restaurant['name']} with {len(restaurant['reviews'])} reviews")
        return restaurant
    
    def run(self):
        """Main collection loop"""
        print("="*60)
        print("QUICK RESTAURANT COLLECTOR")
        print("="*60)
        print("\n🎯 Goal: Add reviews for 10-15 restaurants")
        print("   Aim for 2-3 reviews per restaurant")
        print("="*60)
        
        while True:
            available = self.show_menu()
            
            try:
                choice = int(input(f"\nSelect restaurant (0-{len(self.restaurant_list) + 1}): "))
            except ValueError:
                print("⚠️  Please enter a number")
                continue
            
            if choice == 0:
                # Save and exit
                break
            elif choice == len(self.restaurant_list) + 1:
                # Custom restaurant
                name = input("\nEnter restaurant name: ").strip()
                if not name:
                    continue
                restaurant_info = {"name": name, "cuisine": [], "price_range": "₹₹"}
            elif 1 <= choice <= len(self.restaurant_list):
                restaurant_info = self.restaurant_list[choice - 1]
            else:
                print("⚠️  Invalid choice")
                continue
            
            # Add reviews for this restaurant
            restaurant = self.quick_add_reviews(restaurant_info)
            
            if restaurant:
                # Check if restaurant already exists
                existing_names = [r["name"] for r in self.data["restaurants"]]
                if restaurant["name"] in existing_names:
                    print(f"\n⚠️  {restaurant['name']} already collected!")
                    update = input("Update with new reviews? (y/n): ").lower()
                    if update == 'y':
                        # Find and update
                        for i, r in enumerate(self.data["restaurants"]):
                            if r["name"] == restaurant["name"]:
                                self.data["restaurants"][i]["reviews"].extend(restaurant["reviews"])
                                print(f"✅ Updated {restaurant['name']}")
                                break
                else:
                    self.data["restaurants"].append(restaurant)
                
                # Auto-save after each restaurant
                self.save()
        
        # Final save
        self.save()
        print("\n👋 Collection complete!")
        
        # Show summary
        total_reviews = sum(len(r["reviews"]) for r in self.data["restaurants"])
        print("\n" + "="*60)
        print("FINAL SUMMARY")
        print("="*60)
        print(f"Restaurants: {len(self.data['restaurants'])}")
        print(f"Total reviews: {total_reviews}")
        print(f"Saved to: {self.output_file}")
        print("="*60)
    
    def save(self):
        """Save current data"""
        self.data["metadata"]["total_restaurants"] = len(self.data["restaurants"])
        self.data["metadata"]["total_reviews"] = sum(
            len(r.get("reviews", [])) for r in self.data["restaurants"]
        )
        self.data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        save_json(self.data, self.output_file)
        print(f"💾 Saved! ({len(self.data['restaurants'])} restaurants)")


if __name__ == "__main__":
    collector = QuickCollector("data/restaurant_list.txt")
    collector.run()
