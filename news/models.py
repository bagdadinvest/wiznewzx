from django.db import models

# Create your models here.
from wagtail.models import Page
from wagtail.fields import RichTextField
from django.shortcuts import render
from .services import fetch_bing_news  # Assuming services.py exists in your app
from wagtail.admin.panels import FieldPanel


class NewsIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def serve(self, request):
        query = request.GET.get('q', 'latest')
        news_data = fetch_bing_news(query)  # Fetch Bing News articles
        return render(request, 'news/news_index_page.html', {
            'page': self,
            'news': news_data.get('value', []),
        })
