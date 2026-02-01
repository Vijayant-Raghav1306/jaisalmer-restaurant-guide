"""
Exercise 1: Check robots.txt for websites
Goal: Understand what we're allowed to scrape
"""

import requests
from urllib.parse import urljoin

def check_robots_txt(base_url):
    """
    Check and display robots.txt for a website
    """
    robots_url = urljoin(base_url, '/robots.txt')
    
    print(f"\n{'='*60}")
    print(f"Checking: {robots_url}")
    print('='*60)
    
    try:
        response = requests.get(robots_url, timeout=10)
        
        if response.status_code == 200:
            print("\n✅ robots.txt found!")
            print("\nContent (first 50 lines):")
            print("-" * 60)
            
            lines = response.text.split('\n')[:50]
            for line in lines:
                print(line)
            
            print("\n" + "="*60)
            print("KEY THINGS TO LOOK FOR:")
            print("="*60)
            print("• 'Disallow' = What NOT to scrape")
            print("• 'Allow' = What you CAN scrape")
            print("• 'Crawl-delay' = How long to wait between requests")
            print("="*60)
            
        else:
            print(f"\n⚠️  No robots.txt found (Status: {response.status_code})")
            print("This doesn't mean scraping is allowed - check ToS!")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

# Test different sites
sites_to_check = [
    "https://www.google.com",
    "https://www.tripadvisor.com",
    "https://www.zomato.com",
]

print("="*60)
print("ROBOTS.TXT CHECKER")
print("="*60)
print("\nThis tool helps you understand scraping permissions")

for site in sites_to_check:
    check_robots_txt(site)
    print("\n")

print("="*60)
print("SUMMARY:")
print("="*60)
print("\n1. Always check robots.txt before scraping")
print("2. Respect 'Disallow' directives")
print("3. Follow 'Crawl-delay' if specified")
print("4. When in doubt, use official APIs instead")
print("="*60)
