import json, cloudscraper

scraper = cloudscraper.create_scraper()
data = scraper.get('https://sky.shiiyu.moe/api/v2/bazaar').text
data = json.loads(data)
with open('bazaar.json', 'w') as f:
    json.dump(data, f)