from django.contrib import admin
from django.urls import path
from . import views
# from my_app.views import get_home
urlpatterns = [
    path('home', views.get_home),
    path('ChatWithAI', views.getChatWithAI),
    path('footer', views.getFooter),
    path('header', views.getHeader),
    path('homePage', views.getHomePage),

]
