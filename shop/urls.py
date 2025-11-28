from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    
    # Authentication URLs
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    
    # Purchase
    path('purchase/<int:product_id>/', views.purchase_product, name='purchase_product'),
    
    # Language
    path('language/<str:lang_code>/', views.set_language_view, name='set_language'),
]