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
    list_display = ('name', 'brand', 'product_type', 'size', 'price', 'stock', 'category')
    list_filter = ('category', 'brand', 'product_type', 'size')
    search_fields = ('name', 'brand', 'description')
    list_editable = ('price', 'stock')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'wilaya', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'wilaya', 'created_at')
    search_fields = ('order_number', 'full_name', 'phone', 'address', 'commune')
    list_editable = ('status',)
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'user')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'total_price')
        }),
        ('Customer Info', {
            'fields': ('full_name', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('wilaya', 'commune', 'address', 'postal_code')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


# Re-register Order with inline items
admin.site.unregister(Order)


@admin.register(Order)
class OrderAdminWithItems(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'wilaya', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'wilaya', 'created_at')
    search_fields = ('order_number', 'full_name', 'phone', 'address', 'commune')
    list_editable = ('status',)
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'user')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'total_price')
        }),
        ('Customer Info', {
            'fields': ('full_name', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('wilaya', 'commune', 'address', 'postal_code')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)

@admin.register(MonthlyLeaderboard)
class MonthlyLeaderboardAdmin(admin.ModelAdmin):
    list_display = ('month', 'user', 'points', 'rank')
    list_filter = ('month',)
    ordering = ('month', 'rank')