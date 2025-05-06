import pandas as pd
from decimal import Decimal
from django.utils import timezone
from django.db.models import Count
from store.models import CustomerStats, Category
from store.services.segmentation import predict_rfm_segment, predict_behavioral_segment
from store.services.recommender import recommend_categories_for_user
from store.utils.labels import get_rfm_label, get_behavioral_label


def update_customer_stats(customer):
    # Checks if CustomerStatus exists, otherwise creates it
    stats, created = CustomerStats.objects.get_or_create(customer=customer)

    # Number of interactions
    stats.view_count = customer.viewinteraction_set.count()
    stats.cart_count = customer.cartinteraction_set.count()
    stats.purchase_count = customer.purchaseinteraction_set.count()

    # Total spend (Normal and Discounted)
    purchases = customer.purchaseinteraction_set.select_related('product')
    total_spent = Decimal('0.00')
    discounted_total = Decimal('0.00')

    for purchase in purchases:
        price = Decimal(purchase.product.price)
        discounted_price = purchase.discounted_total_price
        if discounted_price is not None:
            discounted_price = Decimal(discounted_price)
        else:
            discounted_price = price

        total_spent += price
        discounted_total += discounted_price

    stats.monetary = total_spent
    stats.discounted_monetary = discounted_total

    # Recency & Frequency
    if purchases.exists():
        last_purchase = purchases.latest('timestamp')
        stats.recency = (timezone.now() - last_purchase.timestamp).days
        stats.frequency = stats.purchase_count
    else:
        stats.recency = 999
        stats.frequency = 0

    # Most interacted category
    most_common_category = (
        customer.viewinteraction_set
        .values('product__category')
        .annotate(count=Count('product__category'))
        .order_by('-count')
        .first()
    )
    if most_common_category:
        category = Category.objects.filter(id=most_common_category['product__category']).first()
        stats.most_preferred_category = category
    else:
        stats.most_preferred_category = None

    # Segmentation
    rfm_data = pd.DataFrame([{
        'recency': stats.recency,
        'frequency': stats.frequency,
        'monetary': float(stats.monetary)
    }])
    behavioral_data = pd.DataFrame([{
        'view_count': stats.view_count,
        'cart_count': stats.cart_count,
        'purchase_count': stats.purchase_count
    }])

    stats.rfm_segment = get_rfm_label(predict_rfm_segment(rfm_data))
    stats.behavioral_segment = get_behavioral_label(predict_behavioral_segment(behavioral_data))

    # Category suggestion
    favorite_category_name = (
        stats.most_preferred_category.name if stats.most_preferred_category else "Electronics"
    )
    recommended = recommend_categories_for_user(
        stats.view_count,
        stats.cart_count,
        stats.purchase_count,
        favorite_category_name
    )
    stats.recommended_categories = recommended[:3]

    # Save changes
    stats.save(force_update=True)

