import requests
from wagtail.admin.menu import MenuItem
from wagtail import hooks
from django.urls import path, reverse
from django.shortcuts import render
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import logging
import json
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

# API Key
BING_NEWS_API_KEY = settings.BING_NEWS_API_KEY

# Base URL for Bing News API
BASE_URL = "https://api.bing.microsoft.com/v7.0/news"

# Valid categories for en-US
valid_categories = [
    _("Business"), _("Entertainment"), _("Health"), _("Politics"), _("Products"),
    _("ScienceAndTechnology"), _("Sports"), _("Sports_Soccer"), _("Sports_Tennis"),
    _("US"), _("World"), _("World_Africa"), _("World_Americas"), _("World_Asia"),
    _("World_Europe"), _("World_MiddleEast")
]

# Sort options for frontend
sort_options = [_("Date"), _("Relevance")]

# Count options for articles (frontend + backend)
count_options = [20, 50, 100]

def fetch_bing_news_view(request):
    articles = []
    raw_response = None
    error_message = None

    if request.method == 'POST':
        query = request.POST.get('query', None)
        category = request.POST.get('category', None)
        sort_by = request.POST.get('sort_by', 'Relevance')
        count = int(request.POST.get('count', 20))

        headers = {
            "Ocp-Apim-Subscription-Key": BING_NEWS_API_KEY
        }

        params = {
            "count": count,
            "sortBy": sort_by,
            "originalImg": "true"
        }

        try:
            if query:
                params["q"] = query
                params["mkt"] = "en-US"
                endpoint = f"{BASE_URL}/search"
            elif category:
                params["category"] = category
                params["mkt"] = "en-US"
                endpoint = BASE_URL
            else:
                params["q"] = ""
                endpoint = BASE_URL

            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            raw_response = response.json()

            # Extract and format articles
            articles = raw_response.get('value', [])
            for article in articles:
                if 'datePublished' in article:
                    iso_date = article['datePublished']
                    article['formatted_date'] = datetime.fromisoformat(iso_date.replace("Z", "+00:00")).strftime('%d/%m/%Y %H:%M')
                if 'image' in article and 'thumbnail' in article['image']:
                    thumbnail_url = article['image']['thumbnail']['contentUrl']
                    height = article['image']['thumbnail'].get('height', 400)
                    article['resized_thumbnail'] = f"{thumbnail_url}&h={height}&p=0"

        except requests.exceptions.RequestException as e:
            error_message = _("Error fetching news: %(error)s") % {'error': str(e)}
            logger.error(_("Bing News API request failed: %(error)s") % {'error': e})

    context = {
        'articles': articles,
        'raw_response': raw_response,  # Keep raw response available for template (if needed)
        'error_message': error_message,
        'valid_categories': valid_categories,
        'sort_options': sort_options,
        'count_options': count_options
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
        _("Proposals"),
        reverse("fetch_bing_news"),
        icon_name="bold",
        order=102,
    )

NEWS_API_KEY = settings.NEWS_API_KEY

def fetch_news_view(request):
    articles = []
    error_message = None

    # Permanent valid options
    valid_countries = ['us', 'gb', 'fr', 'de', 'it', 'es']
    valid_categories = [
        _('business'), _('entertainment'), _('general'),
        _('health'), _('science'), _('sports'), _('technology')
    ]
    valid_sort_options = [_('relevancy'), _('popularity'), _('publishedAt')]
    news_languages = ['ar', 'fr', 'en', 'it', 'tr', 'he']

    if request.method == 'POST':
        query = request.POST.get('query', '')
        language = request.POST.get('language', '')
        sources = request.POST.get('sources', '')
        from_date = request.POST.get('from', '')
        to_date = request.POST.get('to', '')
        sort_by = request.POST.get('sortBy', 'publishedAt')
        page_size = request.POST.get('pageSize', 20)
        page = request.POST.get('page', 1)

        try:
            response = newsapi.get_everything(
                q=query,
                language=language if language in news_languages else None,
                sources=sources or None,
                from_param=from_date or None,
                to=to_date or None,
                sort_by=sort_by if sort_by in valid_sort_options else 'publishedAt',
                page_size=int(page_size),
                page=int(page)
            )

            # Filter out unwanted articles
            raw_articles = response.get('articles', [])
            articles = [
                {
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'urlToImage': article['urlToImage'],
                    'publishedAt': article['publishedAt'],  # Pass as string
                    'source': article['source']['name']
                }
                for article in raw_articles
                if article['title'] != '[Removed]' and article['description'] != '[Removed]'
                and article['source']['name'] != '[Removed]'
            ]

            logger.debug(_("Filtered Articles: %(articles)s") % {'articles': articles})
        except Exception as e:
            error_message = _("Error fetching NewsAPI data: %(error)s") % {'error': str(e)}
            logger.error(_("News API request failed: %(error)s") % {'error': e})

    context = {
        'articles': articles,
        'error_message': error_message,
        'valid_countries': valid_countries,  # Include valid countries in context
        'valid_categories': valid_categories,  # Include valid categories in context
        'valid_sort_options': valid_sort_options,
        'news_languages': news_languages,
    }

    return render(request, 'admin/fetch_news.html', context)

@hooks.register('register_admin_urls')
def register_fetch_news_url():
    return [
        path('fetch-news/', fetch_news_view, name='fetch_news'),
    ]

# @hooks.register("register_admin_menu_item")
# def register_fetch_news_menu_item():
#     return MenuItem(
#         _("Proposals"),
#         reverse("fetch_news"),
#         icon_name="snippet",
#         order=102,
#     )
