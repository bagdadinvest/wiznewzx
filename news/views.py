from django.shortcuts import render

# Create your views here.
from django.urls import path
from .views import news_view

urlpatterns = [
    path('', news_view, name='news_list'),
]
