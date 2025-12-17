"""
URL configuration for petHealth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.my_app, name='my_app')
Class-based views
    1. Add an import:  from other_app.views import my_app
    2. Add a URL to urlpatterns:  path('', my_app.as_view(), name='my_app')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib import admin
from django.urls import path, include
from my_app import views as my_views

# from my_app.views import get_home
urlpatterns = [
    path('admin/', admin.site.urls),
    path('checkout/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),  # để cuối cùng
    path('accounts/', include('allauth.urls')),
    path('', include('review.urls')),
    path('', include('my_app.urls')),
]

