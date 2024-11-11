import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import json

def setup_chrome_driver(driver_path, headless):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    service = Service(driver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape(url, max_items, price_range, category, preview_option, driver_path, headless):
    driver = setup_chrome_driver(driver_path, headless)
    driver.get(url)
    
    # Implement scraping logic here
    items = []
    # Example logic to scrape items
    # ...

    # Dummy data for demonstration
    items = [
        {"title": "Item 1", "price": 10.0, "category": "TS"},
        {"title": "Item 2", "price": 20.0, "category": "SB"},
        # Add more items here
    ]
    
    # Filter items based on user preferences
    if price_range:
        min_price, max_price = map(float, price_range.split('-'))
        items = [item for item in items if min_price <= item['price'] <= max_price]
    
    if category:
        items = [item for item in items if item['category'] in category.split(',')]
    
    # Preview the data
    if preview_option == 'tabular':
        df = pd.DataFrame(items)
        print(df)
    elif preview_option == 'html':
        html = pd.DataFrame(items).to_html()
        with open('preview.html', 'w') as f:
            f.write(html)
        print("Preview saved to 'preview.html'")
    
    driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Scrape e-commerce products.")
    parser.add_argument('url', type=str, help='The URL of the e-commerce site.')
    parser.add_argument('--max_items', type=int, default=100, help='Maximum number of items to scrape.')
    parser.add_argument('--price_range', type=str, help='Price range to filter items (format: min-max).')
    parser.add_argument('--category', type=str, help='Comma-separated list of categories to include.')
    parser.add_argument('--preview', choices=['tabular', 'html'], default='tabular', help='Preview format for scraped data.')
    parser.add_argument('--driver_path', type=str, required=True, help='Path to the ChromeDriver executable.')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode.')

    args = parser.parse_args()

    scrape(args.url, args.max_items, args.price_range, args.category, args.preview, args.driver_path, args.headless)

if __name__ == "__main__":
    main()
