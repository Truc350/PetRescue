# accounts/views.py
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib import messages
from django.shortcuts import render

from .forms import CustomAuthenticationForm, RegisterForm


class CustomLoginView(LoginView):
    template_name = 'frontend/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = False


def forgot_password(request):
    return render(request, 'frontend/forgot_password.html')


class RegisterView(FormView):
    template_name = 'frontend/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')  # Chuyển về login sau khi đăng ký

    def form_valid(self, form):
        form.save()  # Đã xử lý lưu Profile trong form
        messages.success(self.request, 'Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Vui lòng sửa các lỗi bên dưới.')
        return super().form_invalid(form)
def login_view(request):
    return render(request, 'frontend/login.html')