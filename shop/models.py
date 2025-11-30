from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
import uuid
class CustomUser(AbstractUser):
    points = models.IntegerField(default=0)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='referrals'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Add these lines to fix the conflict
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            # Generate a unique referral code
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)
    
    def generate_referral_code(self):
        # Generate a unique referral code using UUID
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"REF{unique_id}"
    
    def __str__(self):
        return f"{self.username} ({self.points} points)"

# Keep the other models (Category, Product, Order, etc.) the same as before
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    PRODUCT_TYPES = [
        ('shoe', 'Chaussure'),
        ('bijoux', 'Bijoux'),
        ('sac', 'Sac'),
        ('other', 'Autre'),
    ]
    
    SHOE_SIZES = [
        ('36', '36'),
        ('37', '37'),
        ('38', '38'),
        ('39', '39'),
        ('40', '40'),
        ('41', '41'),
        ('42', '42'),
        ('43', '43'),
        ('44', '44'),
        ('45', '45'),
        ('one_size', 'Taille Unique'),
    ]
    
    BIJOUX_SIZES = [
        ('small', 'Petit'),
        ('medium', 'Moyen'),
        ('large', 'Grand'),
        ('one_size', 'Taille Unique'),
    ]
    
    SAC_SIZES = [
        ('small', 'Petit'),
        ('medium', 'Moyen'),
        ('large', 'Grand'),
        ('extra_large', 'Très Grand'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='shoe')
    size = models.CharField(max_length=20, blank=True)
    brand = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.brand}"
    
    def get_size_display(self):
        """Get the appropriate size choices based on product type"""
        if self.product_type == 'shoe':
            return dict(self.SHOE_SIZES).get(self.size, self.size)
        elif self.product_type == 'bijoux':
            return dict(self.BIJOUX_SIZES).get(self.size, self.size)
        elif self.product_type == 'sac':
            return dict(self.SAC_SIZES).get(self.size, self.size)
        return self.size
    
    def get_product_type_icon(self):
        """Get appropriate icon for product type"""
        icons = {
            'shoe': '👟',
            'bijoux': '💎',
            'sac': '👜',
            'other': '🛍️'
        }
        return icons.get(self.product_type, '🛍️')
    
    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default-product.jpg'

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Nouvelle'),
        ('preparation', 'En préparation'),
        ('sent', 'Envoyée'),
        ('delivered', 'Livrée'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class MonthlyLeaderboard(models.Model):
    month = models.DateField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    points = models.IntegerField()
    rank = models.IntegerField()
    
    class Meta:
        unique_together = ['month', 'user']
        ordering = ['month', 'rank']
    
    def __str__(self):
        return f"{self.month.strftime('%B %Y')} - {self.user.username} (Rank {self.rank})"