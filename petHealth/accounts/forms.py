from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Tài khoản",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập username',
            'autofocus': True,
        })
    )

    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu',
        })
    )

    error_messages = {
        'invalid_login': 'Tài khoản hoặc mật khẩu không đúng',
        'inactive': 'Tài khoản đã bị khóa',
    }
