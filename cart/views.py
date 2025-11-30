from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from shop.models import Product

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart.html', {'cart': cart})

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check stock
    if product.stock <= 0:
        messages.error(request, "Désolé, ce produit est en rupture de stock.")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': "Rupture de stock"
            })
        return redirect('product_detail', product_id=product_id)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        # Check if we have enough stock
        if cart_item.quantity >= product.stock:
            messages.warning(request, f"Stock limité! Il ne reste que {product.stock} unité(s) de {product.name}.")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f"Stock limité! Il ne reste que {product.stock} unité(s)."
                })
            return redirect('product_detail', product_id=product_id)
        
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f"{product.name} ajouté au panier!")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'message': f"{product.name} ajouté au panier!"
        })
    
    return redirect('product_detail', product_id=product_id)

@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    
    # If this is a quantity decrease (not complete removal)
    if 'action' in request.POST and request.POST['action'] == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.info(request, f"Quantité de {product_name} diminuée.")
        else:
            cart_item.delete()
            messages.success(request, f"{product_name} retiré du panier!")
    else:
        # Complete removal
        cart_item.delete()
        messages.success(request, f"{product_name} retiré du panier!")
    
    cart = Cart.objects.get(user=request.user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'message': f"{product_name} retiré du panier!"
        })
    
    return redirect('cart')

@login_required
def update_cart_count(request):
    """API endpoint to get current cart count"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return JsonResponse({'cart_count': cart.total_items})