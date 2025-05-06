# store/helpers.py
# helpers.py
import joblib
import os
from django.conf import settings

def load_model(model_name, subdir):
    model_path = os.path.join(settings.BASE_DIR, 'store', subdir, model_name)
    return joblib.load(model_path)




from store.models import (
    ViewInteraction, CartInteraction, PurchaseInteraction, FavoriteInteraction,
    CategoryInteraction
)
from django.utils import timezone

def update_product_and_category_interaction(customer, product, interaction_type):
    category = product.category

    # Category interaction güncelle
    category_interaction, _ = CategoryInteraction.objects.get_or_create(
        customer=customer, category=category
    )
    
    if interaction_type == 'view':
        ViewInteraction.objects.create(customer=customer, product=product)
        category_interaction.view_count += 1
    elif interaction_type == 'cart':
        CartInteraction.objects.create(customer=customer, product=product)
        category_interaction.cart_count += 1
    elif interaction_type == 'purchase':
        PurchaseInteraction.objects.create(customer=customer, product=product)
        category_interaction.purchase_count += 1
    elif interaction_type == 'favorite':
        FavoriteInteraction.objects.create(customer=customer, product=product)

    category_interaction.last_interaction = timezone.now()
    category_interaction.save()
