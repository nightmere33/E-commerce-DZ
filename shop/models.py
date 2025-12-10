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
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('preparation', 'En préparation'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]
    
    WILAYA_CHOICES = [
        ('01', '01 - Adrar'),
        ('02', '02 - Chlef'),
        ('03', '03 - Laghouat'),
        ('04', '04 - Oum El Bouaghi'),
        ('05', '05 - Batna'),
        ('06', '06 - Béjaïa'),
        ('07', '07 - Biskra'),
        ('08', '08 - Béchar'),
        ('09', '09 - Blida'),
        ('10', '10 - Bouira'),
        ('11', '11 - Tamanrasset'),
        ('12', '12 - Tébessa'),
        ('13', '13 - Tlemcen'),
        ('14', '14 - Tiaret'),
        ('15', '15 - Tizi Ouzou'),
        ('16', '16 - Alger'),
        ('17', '17 - Djelfa'),
        ('18', '18 - Jijel'),
        ('19', '19 - Sétif'),
        ('20', '20 - Saïda'),
        ('21', '21 - Skikda'),
        ('22', '22 - Sidi Bel Abbès'),
        ('23', '23 - Annaba'),
        ('24', '24 - Guelma'),
        ('25', '25 - Constantine'),
        ('26', '26 - Médéa'),
        ('27', '27 - Mostaganem'),
        ('28', '28 - M\'Sila'),
        ('29', '29 - Mascara'),
        ('30', '30 - Ouargla'),
        ('31', '31 - Oran'),
        ('32', '32 - El Bayadh'),
        ('33', '33 - Illizi'),
        ('34', '34 - Bordj Bou Arreridj'),
        ('35', '35 - Boumerdès'),
        ('36', '36 - El Tarf'),
        ('37', '37 - Tindouf'),
        ('38', '38 - Tissemsilt'),
        ('39', '39 - El Oued'),
        ('40', '40 - Khenchela'),
        ('41', '41 - Souk Ahras'),
        ('42', '42 - Tipaza'),
        ('43', '43 - Mila'),
        ('44', '44 - Aïn Defla'),
        ('45', '45 - Naâma'),
        ('46', '46 - Aïn Témouchent'),
        ('47', '47 - Ghardaïa'),
        ('48', '48 - Relizane'),
        ('49', '49 - El M\'Ghair'),
        ('50', '50 - El Meniaa'),
        ('51', '51 - Ouled Djellal'),
        ('52', '52 - Bordj Badji Mokhtar'),
        ('53', '53 - Béni Abbès'),
        ('54', '54 - Timimoun'),
        ('55', '55 - Touggourt'),
        ('56', '56 - Djanet'),
        ('57', '57 - In Salah'),
        ('58', '58 - In Guezzam'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Shipping information (Yalidine style)
    full_name = models.CharField(max_length=200, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    phone2 = models.CharField(max_length=20, blank=True, null=True)  # Secondary phone
    wilaya = models.CharField(max_length=2, choices=WILAYA_CHOICES, blank=True, default='')
    commune = models.CharField(max_length=100, blank=True, default='')
    address = models.TextField(blank=True, default='')
    postal_code = models.CharField(max_length=10, blank=True, default='')
    notes = models.TextField(blank=True, null=True)  # Delivery notes
    
    # Order tracking
    order_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            import random
            self.order_number = f"CMD{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def get_wilaya_display_full(self):
        return dict(self.WILAYA_CHOICES).get(self.wilaya, self.wilaya)
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.full_name}"

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