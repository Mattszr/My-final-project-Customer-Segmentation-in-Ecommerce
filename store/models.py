from django.db import models
import datetime
from django.contrib.auth.models import User

# Category of products
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name_plural = 'categories'
from django.db import models
from django.contrib.auth.models import User

# Customers
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True) 
    password = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        creating = self.pk is None  
        
        
        if creating and self.user is None:
            user = User.objects.create(
                username=self.email,  
                email=self.email,
                password=self.password,  
            )
            self.user = user
        
        super().save(*args, **kwargs)  
        
    def __str__(self):
        return f'{self.first_name} {self.last_name}'




class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)  
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/')
    image2 = models.ImageField(upload_to='uploads/products/', blank=True, null=True)
    image3 = models.ImageField(upload_to='uploads/products/', blank=True, null=True)

    is_sale = models.BooleanField(default=False)  
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6)  
    discounted_price = models.DecimalField(default=0, decimal_places=2, max_digits=6, blank=True, null=True)  

    def __str__(self):
        return f'{self.name} {self.price}'

    def get_price(self):
        """Returns the price (discounted or regular)."""
        return self.discounted_price if self.discounted_price else self.price

    def get_total_price(self, quantity):
        """Returns the total price (with the discounted price if available)."""
        return self.get_price() * quantity


# Orders
class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=20, default='', blank=True)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)
    total_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    discounted_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def __str__(self):
        return f'{self.product.name} Order'

# Favorites
class Favorite(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')

    def __str__(self):
        return f'{self.customer} - {self.product}'

# Category Interaction
class CategoryInteraction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    view_count = models.IntegerField(default=0)
    cart_count = models.IntegerField(default=0)
    purchase_count = models.IntegerField(default=0)
    last_interaction = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'category')

    def __str__(self):
        return f'{self.customer} - {self.category}'

# View Interaction
class ViewInteraction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer} viewed {self.product}'

# Cart Interaction
class CartInteraction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer} added {self.product} to cart'

# Purchase Interaction
class PurchaseInteraction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    discounted_total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 

    def __str__(self):
        return f'{self.customer} purchased {self.product}'

# Favorite Interaction
class FavoriteInteraction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer} favorited {self.product}'

from django.db import models

class CustomerStats(models.Model):
    customer = models.OneToOneField('Customer', on_delete=models.CASCADE)

    # RFM 
    recency = models.IntegerField(default=0)
    frequency = models.IntegerField(default=0)
    monetary = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)

    # behav 
    view_count = models.IntegerField(default=0)
    cart_count = models.IntegerField(default=0)
    purchase_count = models.IntegerField(default=0)
    discounted_monetary = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)


    # users mot interaction category
    most_preferred_category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)

    # segmentation 
    rfm_segment = models.CharField(max_length=100, blank=True, null=True)
    behavioral_segment = models.CharField(max_length=100, blank=True, null=True)

    # recommend categories
    recommended_categories = models.JSONField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.customer.email} Stats'

