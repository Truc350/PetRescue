from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm

class CustomLoginView(LoginView):
    template_name = 'frontend/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True  # 👈 quan trọng

from django.shortcuts import render

def forgot_password(request):
    return render(request, 'frontend/forgot_password.html')
