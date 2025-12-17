# accounts/urls.py
from django.urls import path
from . import views

from .views import CustomLoginView, forgot_password, RegisterView  # sẽ tạo view này ở bước sau
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    # Sau này thêm đăng ký, logout, v.v.
    # path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('register/', RegisterView.as_view(), name='register'),
    # path('login/', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
]
