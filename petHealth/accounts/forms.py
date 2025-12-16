from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile   # import model UserProfile để lưu thông tin bổ sung


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


class RegisterForm(UserCreationForm):
    fullname = forms.CharField(
        label="Họ và tên",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nhập họ và tên',
            'class': 'form-control',
        })
    )
    birthday = forms.DateField(
        label="Ngày sinh",
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )
    phone = forms.CharField(
        label="Số điện thoại",
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nhập số điện thoại',
            'class': 'form-control',
        })
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Nhập email',
            'class': 'form-control',
        })
    )
    agree_terms = forms.BooleanField(
        label="Tôi đồng ý với điều khoản và chính sách này",
        required=True,
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # tuỳ chỉnh label và placeholder cho field mặc định
        self.fields['username'].label = 'Tên đăng nhập'
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Nhập vào tên đăng nhập',
            'class': 'form-control',
        })
        self.fields['password1'].label = "Mật khẩu"
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Nhập mật khẩu của bạn',
            'class': 'form-control',
        })
        self.fields['password2'].label = "Nhập lại mật khẩu"
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Nhập lại mật khẩu',
            'class': 'form-control',
        })
        self.fields['password1'].help_text = "Mật khẩu tối thiểu 6 ký tự, có ít nhất một số và một chữ cái"

    def save(self, commit=True):
        # tạo user trước
        user = super().save(commit)
        # tạo hoặc cập nhật profile đi kèm
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'fullname': self.cleaned_data['fullname'],
                'birthday': self.cleaned_data['birthday'],
                'phone': self.cleaned_data['phone'],
            }
        )
        return user
