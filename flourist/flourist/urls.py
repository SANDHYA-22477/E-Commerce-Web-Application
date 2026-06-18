"""
URL configuration for flourist project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
 
from django.contrib import admin
from django.urls import path
from flouristapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # ADMIN
    path('admin/', admin.site.urls),

    # HOME
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),

    # CATEGORY
    path('men/', views.men, name='men'),
    path('women/', views.women, name='women'),
    path('kids/', views.kids, name='kids'),

    # CART
        path('add-to-cart/<str:model>/<int:id>/', views.add_to_cart, name='add_to_cart'),
        path('my-cart/', views.my_cart, name='my_cart'),  
    # PAYMENT
    path('payment/men/<int:id>/', views.men_payment, name='men_payment'),
    path('payment/women/<int:id>/', views.women_payment, name='women_payment'),
    path('payment/kids/<int:id>/', views.kids_payment, name='kids_payment'),
    path('payment/home/<int:id>/', views.home_payment, name='home_payment'),

    # SUCCESS
    path('success/', views.success, name='success'),

    # SEARCH
    path('search/', views.search, name='search'),

    # AUTH
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),

    # ORDERS
    path('orders/', views.orders, name='orders'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # WISHLIST
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:id>/<str:model>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:id>/', views.remove_wishlist, name='remove_wishlist'),

    # TRACKING
    path('tracking/', views.tracking, name='tracking'),
]

# MEDIA + STATIC (ONLY ONCE)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
 