from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required 
from .models import Product, Category
from .models import Customer
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms 
from .forms import SignUpForm
from django.views.decorators.http import require_POST
from store.models import CustomerStats

from store.utils.stats import update_customer_stats
from store.services.segmentation import predict_rfm_segment, predict_behavioral_segment
from store.services.recommender import recommend_categories_for_user
from store.models import Customer, ViewInteraction, CartInteraction, PurchaseInteraction, FavoriteInteraction, Product

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from store.models import FavoriteInteraction
from .serializers import ProductSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductSerializer
from django.http import JsonResponse
from store.models import Favorite, Product, Order
from rest_framework.decorators import api_view 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import requests

from .services.segmentation import predict_rfm_segment, predict_behavioral_segment
from .services.recommender import recommend_categories_for_user
import pandas as pd

from store.utils.labels import get_rfm_label, get_behavioral_label

from store.utils.stats import update_customer_stats

from store.helpers import update_product_and_category_interaction


def home(request):
    customers = Customer.objects.all()
    if not customers:
        print("No customer found!")
    return render(request, 'home.html', {'customers':customers})



def product(request, pk):
    product = Product.objects.get(id=pk)

    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(email=request.user.email)


            # Update part
            update_product_and_category_interaction(customer, product, 'view')
            update_customer_stats(customer)

        except Customer.DoesNotExist:
            pass

    return render(request, 'product.html', {'product': product})






class FavoriteProductsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            customer = Customer.objects.get(email=request.user.email)
            favorites = Favorite.objects.filter(customer=customer)
            products = [fav.product for fav in favorites]
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found.'}, status=404)
        
    
@login_required
def favorites_page(request):
    return render(request, 'favorites.html')







def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index.html')  # Redirect to homepage after signup
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})



class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        if request.user.is_authenticated:
            try:
                customer = Customer.objects.get(email=request.user.email)
                update_customer_stats(customer)
            except Customer.DoesNotExist:
                pass
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


    
def index(request):
    products = Product.objects.all()

    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(email=request.user.email)
            update_customer_stats(customer)  # updating the customer stats
        except Customer.DoesNotExist:
            pass

    return render(request, 'index.html', {'products': products})

def apindex(request):
    products = Product.objects.all()
    return render(request, 'apindex.html', {'products':products} )

def category(request, foo):
    foo = foo.replace('-', '')
    try:
        category = Category.objects.get(name=foo)
        product = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':product, 'category':category})
    except:
        messages.success(request, ("The Category does not exist"))
        return redirect('index')

def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories': categories})

# views.py
def category_products(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    products = Product.objects.filter(category=category)
    return render(request, 'store/category_products.html', {
        'category': category,
        'products': products
    })


def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Username and password required.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            print("successful")
            return redirect('index')
        else:
            messages.error(request, "Username or password is incorrect.")
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.success(request, (" You Logged out"))
    return redirect('apindex')



@login_required
@login_required
def user_profile(request):
    user = request.user
    try:
        # personal info
        customer = Customer.objects.get(email=user.email)
        
        customer_stats, created = CustomerStats.objects.get_or_create(customer=customer)

        customer_stats = customer.customerstats

        # Fav product
        favorite_products = Product.objects.filter(favorite__customer=customer)

        # purch history
        purchase_history = Order.objects.filter(customer=customer).order_by('-date')

        has_raw_data = (
            customer_stats.view_count > 0 or
            customer_stats.cart_count > 0 or
            customer_stats.purchase_count > 0
        )

        # Personalisation
        personalization = {
            'user_id': customer.id,
            'recency': customer_stats.recency,
            'frequency': customer_stats.frequency,
            'monetary': customer_stats.monetary,
            'view_count': customer_stats.view_count,
            'cart_count': customer_stats.cart_count,
            'purchase_count': customer_stats.purchase_count,
            'rfm_segment': customer_stats.rfm_segment,
            'behavior_segment': customer_stats.behavioral_segment,
            'favorite_category': customer_stats.most_preferred_category,
            'recommended_categories': customer_stats.recommended_categories,
            'updated_at': customer_stats.updated_at,
        }

        # Prepare context data to be used in Templete
        context = {
            'user': user,
            'personalization': personalization,
            'favorite_products': favorite_products,
            'has_raw_data': has_raw_data,
            'purchase_history': purchase_history,  
        }
        return render(request, 'user_profile.html', context)

    except Customer.DoesNotExist:
        return render(request, 'user_profile.html', {'error': 'Customer could not find.'})  





def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request,("You have registered"))
            return redirect('index')
        else:
            messages.success(request,("Got an Error"))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form':form})
    




@login_required
@require_POST
def favorite_toggle(request):
    user = request.user
    product_id = request.POST.get('product_id')

    if not product_id:
        return JsonResponse({'error': 'No product ID provided'}, status=400)

    try:
        customer, _ = Customer.objects.get_or_create(
            email=user.email,
            defaults={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'password': user.password,  
            }
        )
    except Exception as e:
        return JsonResponse({'error': f'Customer error: {str(e)}'}, status=500)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    favorite, created = Favorite.objects.get_or_create(customer=customer, product=product)

    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    else:
        return JsonResponse({'status': 'added'})





def rfm_segment_view(request):
    segment = None
    label = None

    if request.method == 'POST':
        recency = int(request.POST.get('recency'))
        frequency = int(request.POST.get('frequency'))
        monetary = float(request.POST.get('monetary'))

        df = pd.DataFrame([[recency, frequency, monetary]], columns=['recency', 'frequency', 'monetary'])
        segment = predict_rfm_segment(df)
        label = get_rfm_label(segment)

    return render(request, 'store/rfm_segment.html', {
        'segment': segment,
        'label': label
    })

def behavioral_segment_view(request):
    segment = None
    label = None

    if request.method == 'POST':
        views = int(request.POST.get('views'))
        carts = int(request.POST.get('carts'))
        purchases = int(request.POST.get('purchases'))

        df = pd.DataFrame([[views, carts, purchases]], columns=['views', 'carts', 'purchases'])
        segment = predict_behavioral_segment(df)
        label = get_behavioral_label(segment)

    return render(request, 'store/behavioral_segment.html', {
        'segment': segment,
        'label': label
    })

def recommend_view(request):
    recommendations = None

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        recommendations = recommend_categories_for_user(user_id)

    return render(request, 'store/recommend.html', {
        'recommendations': recommendations
    })


def product_favorited(customer, product):
    FavoriteInteraction.objects.create(customer=customer, product=product)

# user segmentation
def get_user_segments(customer):
    stats = customer.customerstats
    rfm_data = pd.DataFrame([[stats.recency, stats.frequency, float(stats.monetary)]], columns=['recency', 'frequency', 'monetary'])
    rfm_segment = predict_rfm_segment(rfm_data)
    rfm_label = get_rfm_label(rfm_segment)

    behavioral_data = pd.DataFrame([[stats.view_count, stats.cart_count, stats.purchase_count]], columns=['view_count', 'cart_count', 'purchase_count'])
    behavioral_segment = predict_behavioral_segment(behavioral_data)
    behavioral_label = get_behavioral_label(behavioral_segment)

    return {
        'rfm_segment': rfm_label,
        'behavioral_segment': behavioral_label
    }

def get_user_recommendations(customer):
    return recommend_categories_for_user(customer.id)


def search(request):
    query = request.GET.get('q', '')
    if query:
        results = Product.objects.filter(name__icontains=query)  # search
    else:
        results = Product.objects.all()
    
    return render(request, 'search_results.html', {'results': results, 'query': query})



