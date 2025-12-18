from django.contrib import admin
from django.urls import path
from . import views
from django.urls import path
from .views import profile_view
from django.contrib.auth.views import LogoutView

# from my_app.views import get_home
urlpatterns = [
    path("search/", views.search_view, name="search"),
    path('ChatWithAI', views.getChatWithAI),
    path('footer', views.getFooter),
    path('header', views.getHeader),
    path("search/suggest/", views.search_suggest, name="search-suggest"),
    path('logout/', LogoutView.as_view(), name='logout'),

    # path('login/', views.getLogin, name='login'),
    path('register', views.getRegister, name='register'),
    path('forgot-password', views.getForgotPassword),
    path('payment', views.getPayment),
    path('payment-infor', views.getPaymentInfor, name='payment'),
    path('category', views.getCategory, name='category'),
    path('categoryManage', views.getCategoryManage),
    path("support/", views.getSupport, name="support"),
    path('customerManage', views.getCustomerManage),
    path('productManagement', views.getProductManagement),
    path('overviewAdmin', views.getProfileAdmin),
    path('DogKibbleView', views.getDogKibbleView),
    path('personal-page', profile_view, name='personal-page'),
    path('', views.getHomePage, name='homePage'),  # root
    path('homePage/', views.getHomePage, name='homePage'),
    path("profile/", views.profile_view, name="profile"),

    path('dashboard', views.getDashBoard),
    path('health-dog', views.getHealthDog),
    path('policy-purchases', views.getPolicy, name='policy-purchases'),
    path('cat-food', views.getCatFood),
    path('health-cat', views.getHealthCat),
    path('cat-toilet', views.getCatToilet, name='cat-toilet'),
    path('promotion', views.getPromotion, name='promotion'),
    path('detailProduct', views.getDetailProduct, name='detailProduct'),
    path('promotion-manage', views.getPromotionManage),
    path('statistics', views.getStatistic),
    path('dogHygiene', views.getDogHygiene),
    path('wishlist', views.wishlist, name='wishlist'),
    path('shoppingcart', views.shoppingcart, name='shoppingcart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-cart/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path("cart/remove-multiple/", views.remove_multiple_cart, name="remove_multiple_cart"),
    path('delivery-infor', views.getPaymentInfor, name='delivery-infor'),
    path('categories/<slug:slug>/', views.category_view, name="category-detail"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path(
        "wishlist/toggle/<int:product_id>/",
        views.toggle_wishlist_ajax,
        name="toggle-wishlist"
    ),

    path(
        "wishlist/",
        views.wishlist,
        name="wishlist"
    ),
    path(
        "wishlist/remove/<int:product_id>/",
        views.remove_from_wishlist,
        name="remove-wishlist"
    ),

]
