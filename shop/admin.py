from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product, Order, OrderItem, MonthlyLeaderboard

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'points', 'referral_code', 'referred_by', 'created_at')
    list_filter = ('referred_by', 'created_at')
    fieldsets = UserAdmin.fieldsets + (
        ('Points System', {
            'fields': ('points', 'referral_code', 'referred_by')
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'size', 'price', 'stock', 'category')
    list_filter = ('category', 'brand', 'size')
    search_fields = ('name', 'brand', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)

@admin.register(MonthlyLeaderboard)
class MonthlyLeaderboardAdmin(admin.ModelAdmin):
    list_display = ('month', 'user', 'points', 'rank')
    list_filter = ('month',)
    ordering = ('month', 'rank')