from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.conf import settings
from .models import Cart, CartItem
from shop.models import Product, Order, OrderItem

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


@login_required
def checkout(request):
    """Display checkout page with shipping form"""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if cart.items.count() == 0:
        messages.warning(request, "Votre panier est vide.")
        return redirect('cart')
    
    # Get wilaya choices for the form
    wilaya_choices = Order.WILAYA_CHOICES
    
    # Generate CAPTCHA
    import random
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    captcha_answer = num1 + num2
    request.session['captcha_answer'] = captcha_answer
    
    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'wilaya_choices': wilaya_choices,
        'captcha_num1': num1,
        'captcha_num2': num2,
    })


@login_required
@require_POST
def confirm_order(request):
    """Process the order form and create order"""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if cart.items.count() == 0:
        messages.error(request, "Votre panier est vide.")
        return redirect('cart')
    
    # Get form data
    full_name = request.POST.get('full_name', '').strip()
    phone = request.POST.get('phone', '').strip()
    wilaya = request.POST.get('wilaya', '').strip()
    commune = request.POST.get('commune', '').strip()
    address = request.POST.get('address', '').strip()
    postal_code = request.POST.get('postal_code', '').strip()
    notes = request.POST.get('notes', '').strip()
    captcha_input = request.POST.get('captcha', '').strip()
    
    # Basic validation
    errors = []
    if not full_name:
        errors.append("Le nom complet est obligatoire.")
    if not phone:
        errors.append("Le numéro de téléphone est obligatoire.")
    elif not phone.replace(' ', '').replace('+', '').isdigit():
        errors.append("Le numéro de téléphone n'est pas valide.")
    if not wilaya:
        errors.append("La wilaya est obligatoire.")
    if not commune:
        errors.append("La commune est obligatoire.")
    if not address:
        errors.append("L'adresse est obligatoire.")
    
    # Verify CAPTCHA
    captcha_answer = request.session.get('captcha_answer')
    if not captcha_input:
        errors.append("Veuillez résoudre le captcha.")
    elif captcha_answer is None:
        errors.append("Session expirée. Veuillez réessayer.")
    else:
        try:
            if int(captcha_input) != captcha_answer:
                errors.append("Réponse captcha incorrecte.")
        except ValueError:
            errors.append("Réponse captcha invalide.")
    
    if errors:
        wilaya_choices = Order.WILAYA_CHOICES
        # Generate new CAPTCHA for retry
        import random
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        request.session['captcha_answer'] = num1 + num2
        return render(request, 'cart/checkout.html', {
            'cart': cart,
            'wilaya_choices': wilaya_choices,
            'errors': errors,
            'form_data': request.POST,
            'captcha_num1': num1,
            'captcha_num2': num2,
        })
    
    # Clear CAPTCHA from session
    if 'captcha_answer' in request.session:
        del request.session['captcha_answer']
    
    # Create the order
    order = Order.objects.create(
        user=request.user,
        total_price=cart.total_price,
        full_name=full_name,
        phone=phone,
        wilaya=wilaya,
        commune=commune,
        address=address,
        postal_code=postal_code,
        notes=notes if notes else None,
        status='pending'
    )
    
    # Create order items and update stock
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
        # Reduce stock
        item.product.stock = max(0, item.product.stock - item.quantity)
        item.product.save()
    
    # Add points to user
    request.user.points += cart.total_items
    request.user.save()
    
    # Clear cart
    cart.items.all().delete()
    
    messages.success(request, f"Votre commande #{order.order_number} a été confirmée!")
    return redirect('checkout_success', order_number=order.order_number)


@login_required
def checkout_success(request, order_number):
    """Display order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'cart/checkout_success.html', {'order': order})


@login_required
def checkout_cancel(request):
    """Handle cancelled checkout"""
    return render(request, 'cart/checkout_cancel.html')

