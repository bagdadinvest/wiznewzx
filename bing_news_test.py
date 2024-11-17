import requests
import logging

# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Replace with your actual Bing News Search API Key
BING_NEWS_API_KEY = "702932b1edfb464da5382547f8595869"

# Base URL for Bing News API
BASE_URL = "https://api.bing.microsoft.com/v7.0/news"

def fetch_news(query=None, category=None, count=20, sort_by="Relevance"):
    headers = {
        "Ocp-Apim-Subscription-Key": BING_NEWS_API_KEY
    }
    params = {
        "count": count,
        "sortBy": sort_by
    }

    if query:
        params["q"] = query
        endpoint = f"{BASE_URL}/search"
    elif category:
        params["category"] = category
        params["mkt"] = "en-US"
        endpoint = BASE_URL
    else:
        # Default to top stories
        params["q"] = ""
        endpoint = f"{BASE_URL}/search"

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()  # Raise error for non-200 status codes
        data = response.json()

        articles = data.get("value", [])
        for article in articles:
            print(f"Title: {article.get('name')}")
            print(f"URL: {article.get('url')}")
            print(f"Description: {article.get('description')}\n")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news: {e}")

if __name__ == "__main__":
    # Test query
    print("Fetching news with query 'trump':")
    fetch_news(query="trump")

    # Test category
    print("\nFetching news in 'Health' category:")
    fetch_news(category="Health")

    # Test top stories
    print("\nFetching top news stories:")
    fetch_news()
