# store/tasks.py
from celery import shared_task
from store.models import Customer
from store.utils.stats import update_customer_stats

@shared_task
def update_all_customer_stats():
    for customer in Customer.objects.all():
        update_customer_stats(customer)
