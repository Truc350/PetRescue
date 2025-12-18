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
    # path('forgot_password/', forgot_password, name='forgot-password'),
    path('register/', RegisterView.as_view(), name='register'),
    # path('login/', views.login_view, name='login'),
    # path('login/', views.login_view, name='login'),

    #     flow qune matkhau
    # 1. Nhập email
    path('forgot_password/', auth_views.PasswordResetView.as_view(
        template_name='frontend/forgot_password.html',
        email_template_name='frontend/password_reset_email.html',
        success_url='/accounts/forgot_password/done/'
    ), name='forgot-password'),

    # 2. Đã gửi email
    path('forgot_password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='frontend/password_reset_done.html'
    ), name='password_reset_done'),

    # 3. Nhập mật khẩu mới
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='frontend/create-new-password.html',
        success_url='/accounts/reset/done/'
    ), name='password_reset_confirm'),

    # 4. Hoàn tất
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='frontend/password_reset_complete.html'
    ), name='password_reset_complete'),

]
