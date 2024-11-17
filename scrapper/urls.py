from django.urls import path
from .views import scrape_and_create_proposal

urlpatterns = [
    path('scrape/', scrape_and_create_proposal, name='scrape_and_create_proposal'),
]
