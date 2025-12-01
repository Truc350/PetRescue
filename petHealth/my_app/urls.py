from django.contrib import admin
from django.urls import path
from . import views

# from my_app.views import get_home
urlpatterns = [
    path('home', views.get_home),
    path('ChatWithAI', views.getChatWithAI),
    path('footer', views.getFooter),
    path('header', views.getHeader),
    path('login', views.getLogin),
    path('register', views.getRegister),
    path('forgot-password', views.getForgotPassword),
    path('payment', views.getPayment),
    path('payment-infor', views.getPaymentInfor),
    path('category', views.getCategory),
    path('categoryManage', views.getCategoryManage),
    path('customerManage', views.getCustomerManage),
    path('productManagement', views.getProductManagement),
    path('overviewAdmin', views.getProfileAdmin),
    path('DogKibbleView', views.getDogKibbleView),
    path('personal-page', views.getPersonal),
    path('homePage', views.getHomePage),
    path('dashboard', views.getDashBoard),
]
