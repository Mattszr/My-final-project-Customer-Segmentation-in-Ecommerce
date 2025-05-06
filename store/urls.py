from django.urls import path
from . import views
from .views import ProductListView
from .views import FavoriteProductsAPIView
from .views import favorites_page , category_summary


urlpatterns = [
    path('home/', views.home, name='home'),
    path('index', views.index, name='index'),
    path('api/products/', ProductListView.as_view(), name='api-products'),
    path('apindex', views.apindex, name='apindex'),
    path('store/templates/login', views.login_user, name='login_user'),
    path('logout', views.logout_user, name='logout_user'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('register', views.register_user, name='register'),
    path('product/<int:pk>', views.product, name='product'),
    path('category/<str:foo>', views.category, name='category'),
    path('category_summary/', views.category_summary, name='category_summary'),
    path('favorite-toggle/', views.favorite_toggle, name='favorite_toggle'),
    path('search/', views.search, name='search'),
    path('api/favorites/', FavoriteProductsAPIView.as_view(), name='favorite-products'),
    path('favorites/', views.favorites_page, name='favorites-page'),
    path('category/<int:category_id>/', views.category_products, name='category'),

]
