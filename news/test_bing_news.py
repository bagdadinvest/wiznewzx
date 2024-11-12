import requests

def fetch_bing_news(query):
    api_key = '702932b1edfb464da5382547f8595869'  # Replace with your actual API key
    endpoint = 'https://api.bing.microsoft.com/v7.0/news/search'
    headers = {'Ocp-Apim-Subscription-Key': api_key}
    params = {'q': query, 'count': 10, 'mkt': 'en-US'}

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()  # Raise error for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Test the function
if __name__ == "__main__":
    query = input("Enter search query: ")
    news_data = fetch_bing_news(query)

    if news_data:
        for article in news_data.get('value', []):
            print(f"Title: {article['name']}")
            print(f"Description: {article['description']}")
            print(f"URL: {article['url']}")
            print("-" * 50)
    else:
        print("No news articles found or API error.")
