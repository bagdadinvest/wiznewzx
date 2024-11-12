import requests

def fetch_bing_news(query):
    """
    Fetch news articles using Bing News Search API.
    """
    api_key = '702932b1edfb464da5382547f8595869'  # Replace with your API key
    endpoint = 'https://api.bing.microsoft.com/v7.0/news/search'
    headers = {'Ocp-Apim-Subscription-Key': api_key}
    params = {'q': query, 'count': 10, 'mkt': 'en-US'}

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return None
