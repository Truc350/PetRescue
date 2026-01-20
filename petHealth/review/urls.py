from django.urls import path
from . import views

urlpatterns = [
    path("review/add/<slug:slug>/", views.add_review, name="add_review"),
    path("product/<slug:slug>/sentiment-chart/",
         views.sentiment_chart,
         name="sentiment_chart"),
    path('product/<slug:slug>/sentiment/', views.sentiment_summary, name='sentiment_summary'),
]