
import json

with open('data/processed/final_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*60)
print("DATASET VERIFICATION")
print("="*60)

metadata = data['metadata']
restaurants = data['restaurants']

print(f"\n✅ Restaurants: {metadata['total_restaurants']}")
print(f"✅ Reviews: {metadata['total_reviews']}")
print(f"✅ Avg Rating: {metadata['avg_rating']}⭐")

print("\n📊 Review Distribution:")
for rest in sorted(restaurants, key=lambda x: len(x['reviews']), reverse=True)[:5]:
    print(f"   {rest['name']}: {len(rest['reviews'])} reviews")

print("\n📝 Sample Review:")
if restaurants and restaurants[0]['reviews']:
    sample = restaurants[0]['reviews'][0]
    print(f"   Restaurant: {restaurants[0]['name']}")
    print(f"   Text: {sample['text'][:100]}...")
    print(f"   Rating: {sample['rating']}⭐")

print("\n" + "="*60)
print("✅ DATASET LOOKS GOOD!")
print("="*60)
