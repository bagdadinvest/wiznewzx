import os
import requests
import logging
import mimetypes
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
import django
from django.conf import settings

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newspro.settings.base")  # Replace with your project name
django.setup()

def sanitize_url(url):
    """Sanitize URL by removing trailing invalid characters."""
    if url:
        sanitized_url = url.strip().rstrip("',")
        logging.debug(f"Sanitized URL: {sanitized_url}")
        return sanitized_url
    return None

def download_image(url):
    """Download an image and save it temporarily to debug issues."""
    url = sanitize_url(url)
    if not url or not url.startswith("http"):
        logging.warning(f"Invalid sanitized image URL: {url}")
        return None

    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Determine the file extension
            content_type = response.headers.get('Content-Type')
            extension = mimetypes.guess_extension(content_type) or os.path.splitext(urlparse(url).path)[-1]

            if not extension:
                extension = ".jpg"  # Default to .jpg if extension cannot be determined

            temp_file = NamedTemporaryFile(delete=False, suffix=extension)
            for chunk in response.iter_content(1024):
                temp_file.write(chunk)
            temp_file.seek(0)

            logging.info(f"Image downloaded and temporarily saved: {temp_file.name}")
            return temp_file.name
        else:
            logging.error(f"Failed to download image, HTTP Status: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Image download failed: {e}")
        return None

def fetch_news_articles():
    """Fetch news articles from News API."""
    api_key = getattr(settings, "NEWS_API_KEY", None)  # Fetch API key from settings
    if not api_key:
        logging.error("News API key not found in settings.")
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "technology",  # Change the query as needed
        "apiKey": api_key,
        "pageSize": 5,  # Limit the number of articles for testing
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        logging.info(f"Fetched {len(articles)} articles.")
        return articles
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news articles: {e}")
        return []

def simulate_image_download_from_api():
    """Simulate downloading images from News API response."""
    articles = fetch_news_articles()

    for article in articles:
        image_url = article.get("urlToImage")
        if image_url:
            logging.info(f"Attempting to download image from URL: {image_url}")
            downloaded_image_path = download_image(image_url)

            if downloaded_image_path:
                logging.info(f"Image successfully downloaded: {downloaded_image_path}")
            else:
                logging.error("Image download failed.")
        else:
            logging.warning("No image URL found for this article.")

if __name__ == "__main__":
    simulate_image_download_from_api()
