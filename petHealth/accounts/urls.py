# accounts/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
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

    #     flow qune matkhau
    path(
        'forgot-password/',
        auth_views.PasswordResetView.as_view(
            template_name='frontend/forgot-password.html',
            email_template_name='frontend/password_reset_email.html',
            success_url='/accounts/login/'  # 🔥 quay thẳng về login
        ),
        name='forgot-password'
    ),

    # Create new password
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='frontend/create-new-password.html',
            success_url='/accounts/login/'  # 🔥 đổi xong quay về login
        ),
        name='password_reset_confirm'
    ),

    # Quên mật khẩu – nhập email
    path(
        'forgot-password/',
        auth_views.PasswordResetView.as_view(
            template_name='frontend/forgot-password.html',
            email_template_name='frontend/password_reset_email.html',
            success_url='/accounts/login/'
        ),
        name='forgot-password'
    ),

    # Tạo mật khẩu mới
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='frontend/create-new-password.html',
            success_url='/accounts/login/'
        ),
        name='password_reset_confirm'
    ),

]
