from django.shortcuts import render, get_object_or_404, redirect
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from store.models import Product, Customer, Order, CustomerStats
from store.utils.stats import update_customer_stats
from store.helpers import update_product_and_category_interaction
from django.utils import timezone
from store.utils.discounts import calculate_discounted_total  # discount
from store.models import Customer
from store.utils.discounts import calculate_discounted_total, RFM_DISCOUNT_MAP
from decimal import Decimal
from django.contrib import messages 
from django.contrib.auth.decorators import login_required



@login_required
def cart_checkout(request):
    cart = Cart(request)

    if request.user.is_authenticated:
        try:
            
            customer, created = Customer.objects.get_or_create(
                user=request.user,
                defaults={
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'email': request.user.email
                }
            )

            
            if not hasattr(customer, 'customerstats'):
                
                customerstats = CustomerStats.objects.create(customer=customer)

            
            segment = getattr(customer.customerstats, 'rfm_segment', None)
            discount_rate = RFM_DISCOUNT_MAP.get(segment, Decimal("0.00"))

            
            address = customer.address  
            phone = customer.phone  

            
            for product in cart.get_prods():
                quantity = cart.get_quants().get(str(product.id), 1)

                unit_price = product.price
                discounted_price = product.sale_price if product.is_sale else unit_price
                discounted_price *= (1 - discount_rate)  

                
                Order.objects.create(
                    product=product,
                    customer=customer,
                    quantity=quantity,
                    address='address',
                    phone='phone',
                    date=timezone.now().date(),
                    status=True,
                    total_price=unit_price * quantity,
                    discounted_total_price=discounted_price * quantity
                )

            
                update_product_and_category_interaction(customer, product, 'purchase')
                update_customer_stats(customer)

            
            cart.clear()

             
            return render(request, 'checkout_success.html', {
                'quantities': cart.get_quants(),
                'products': cart.get_prods(),
            })

        except Customer.DoesNotExist:
            messages.error(request, "You cannot proceed with checkout without logging in.")  
            return redirect('cart_summary') 

    messages.error(request, "You cannot proceed with checkout without logging in.")  
    return redirect('cart_summary') 




def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods()  
    quantities = cart.get_quants()  # Quantities of products in the basket

    total, _ = cart.cart_total() 
    discounted_total = total
    discount_amount = 0
    discount_rate = 0

    # Apply discount if user is logged in
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(email=request.user.email)  # find the cutomer
            #Calculate the price of the items in the cart with the get_price function
            discounted_total, discount_amount, discount_rate = calculate_discounted_total(
                customer, 
                cart_products,
                quantities
            )
        except Customer.DoesNotExist:
            pass  # If customer is not found do nothing

    return render(request, "cart_summary.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "total": total,
        "discounted_total": discounted_total,
        "discount_amount": discount_amount,
        "discount_rate": int(discount_rate * 100),
    })





def cart_add(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id')) 
        product_qty = int(request.POST.get('product_qty')) 
        product = get_object_or_404(Product, id=product_id)

        # add product
        cart.add(product=product, quantity=product_qty)

        # updated 
        cart_quantity = cart.__len__()

        # save
        if request.user.is_authenticated:
            try:
                customer = Customer.objects.get(email=request.user.email)

                # save
                update_product_and_category_interaction(customer, product, 'cart')

            except Customer.DoesNotExist:
                pass

        # total
        response = JsonResponse({'qty': cart_quantity})
        return response


def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product=product_id)
        response = JsonResponse({'product':product_id})
        return response

def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id')) 
        product_qty = int(request.POST.get('product_qty'))
        cart.update(product=product_id, quantity=product_qty)
        response = JsonResponse({'qty':product_qty})
        
        #return redirect('cart_summary')
        return response