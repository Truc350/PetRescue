from django.urls import path
from . import views

urlpatterns = [
    path("review/add/<int:product_id>/", views.add_review, name="add_review"),
    path("product/<int:product_id>/sentiment-chart/",
         views.sentiment_chart,
         name="sentiment_chart"),
    path('product/<int:product_id>/sentiment/', views.sentiment_summary, name='sentiment_summary'),
]