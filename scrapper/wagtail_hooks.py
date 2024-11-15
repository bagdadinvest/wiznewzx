from wagtail.admin.menu import MenuItem, Menu
from wagtail import hooks
from django.urls import path, reverse
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import requests
import logging
from django.utils.translation import gettext_lazy as _  # For translations

# Setup logging
logger = logging.getLogger(__name__)

BING_NEWS_API_KEY = settings.BING_NEWS_API_KEY  # Ensure you add this in your settings

def fetch_bing_news_view(request):
    articles = []
    error_message = None

    if request.method == 'POST':
        # Capture form parameters
        query = request.POST.get('query', '')
        cc = request.POST.get('cc', '')
        category = request.POST.get('category', '')
        freshness = request.POST.get('freshness', '')
        count = request.POST.get('count', 10)
        offset = request.POST.get('offset', 0)
        mkt = request.POST.get('mkt', '')
        setLang = request.POST.get('setLang', '')
        originalImg = request.POST.get('originalImg', False)  # Correct boolean
        safeSearch = request.POST.get('safeSearch', 'Moderate')
        sortBy = request.POST.get('sortBy', 'Relevance')

        # Define API endpoint URL
        url = "https://api.bing.microsoft.com/v7.0/news/search"

        # Build parameters dict only for non-empty values
        params = {
            'q': query,
            'cc': cc,
            'category': category,
            'freshness': freshness,
            'count': count,
            'offset': offset if offset else None,
            'mkt': mkt if mkt else None,
            'setLang': setLang if setLang else None,
            'originalImg': 'true' if originalImg else 'false',
            'safeSearch': safeSearch,
            'sortBy': sortBy,
        }

        # Remove keys with None values
        params = {k: v for k, v in params.items() if v}

        headers = {
            'Ocp-Apim-Subscription-Key': BING_NEWS_API_KEY,
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            articles = response.json().get('value', [])
        except requests.exceptions.RequestException as e:
            error_message = f"Error fetching news: {str(e)}"
            logger.error(f"Bing News API request failed: {e}")
        except ValueError as e:
            error_message = "Error parsing response. Please try again later."
            logger.error(f"Response parsing error: {e}")

    context = {
        'articles': articles,
        'error_message': error_message,
    }

    return render(request, 'admin/fetch_bing_news.html', context)


@hooks.register('register_admin_urls')
def register_bing_news_fetch_url():
    return [
        path('fetch-bing-news/', fetch_bing_news_view, name='fetch_bing_news'),
    ]


@hooks.register("register_admin_menu_item")
def register_fetch_bing_news_menu_item():
    return MenuItem(
        _("Fetch Bing News"),
        reverse("fetch_bing_news"),
        icon_name="bold",
        order=101,
    )



NEWS_API_KEY = settings.NEWS_API_KEY

def fetch_news_view(request):
    articles = []
    error_message = None

    if request.method == 'POST':
        query = request.POST.get('query', '')
        language = request.POST.get('language', '')
        sort_by = request.POST.get('sortBy', 'publishedAt')
        from_date = request.POST.get('from', '')
        to_date = request.POST.get('to', '')
        sources = request.POST.get('sources', '')
        page_size = request.POST.get('pageSize', 10)

        url = "https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'language': language,
            'sortBy': sort_by,
            'from': from_date,
            'to': to_date,
            'sources': sources,
            'pageSize': page_size,
            'apiKey': NEWS_API_KEY
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            raw_articles = response.json().get('articles', [])

            # Filter out articles marked as "[Removed]"
            articles = [
                article for article in raw_articles
                if not (article.get('title') == '[Removed]' or article.get('description') == '[Removed]' or article.get('source', {}).get('name') == '[Removed]')
            ]
        except requests.exceptions.RequestException as e:
            error_message = f"Error fetching news: {str(e)}"
            logger.error(f"News API request failed: {e}")
        except ValueError as e:
            error_message = "Error parsing response. Please try again later."
            logger.error(f"Response parsing error: {e}")

    context = {
        'articles': articles,
        'error_message': error_message,
    }

    return render(request, 'admin/fetch_news.html', context)

@hooks.register('register_admin_urls')
def register_fetch_news_url():
    return [
        path('fetch-news/', fetch_news_view, name='fetch_news'),
    ]

@hooks.register("register_admin_menu_item")
def register_fetch_news_menu_item():
    return MenuItem(
        _("Fetch News"),
        reverse("fetch_news"),
        icon_name="snippet",
        order=102,
    )



