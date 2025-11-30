from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from .models import Product, Category, CustomUser, Order, OrderItem
from .forms import CustomUserCreationForm, CustomLoginForm
from django.utils import translation
from django.http import HttpResponseRedirect
from django.db.models import Q, Sum


def set_language_view(request, lang_code):
    if lang_code in ['fr', 'en', 'ar']:
        translation.activate(lang_code)
        request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    
    # Redirect back to the previous page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    else:
        return HttpResponseRedirect('/')



def home(request):
    featured_products = Product.objects.filter(stock__gt=0)[:6]
    top_users = CustomUser.objects.order_by('-points')[:3]  # Top 3 for homepage
    
    context = {
        'featured_products': featured_products,
        'top_users': top_users,
    }
    return render(request, 'home.html', context)

def products(request):
    categories = Category.objects.all()
    products_list = Product.objects.filter(stock__gt=0)
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        products_list = products_list.filter(category_id=category_id)
        current_category = Category.objects.get(id=category_id)
    else:
        current_category = None
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )
    
    # Calculate totals in the view, not template
    total_products = products_list.count()
    total_categories = categories.count()
    total_stock = products_list.aggregate(total_stock=Sum('stock'))['total_stock'] or 0
    
    context = {
        'products': products_list,
        'categories': categories,
        'current_category': current_category,
        'total_products': total_products,
        'total_categories': total_categories,
        'total_stock': total_stock,
    }
    return render(request, 'products.html', context)

def leaderboard(request):
    # Get top 10 users by points for current month
    top_users = CustomUser.objects.order_by('-points')[:10]
    
    # Get total users and total points in system
    total_users = CustomUser.objects.count()
    total_points = CustomUser.objects.aggregate(Sum('points'))['points__sum'] or 0
    
    context = {
        'top_users': top_users,
        'total_users': total_users,
        'total_points': total_points,
    }
    return render(request, 'leaderboard.html', context)

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
    else:
        form = CustomLoginForm()
    
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Auto-login after registration
            login(request, user)
            
            # Success message with referral info if applicable
            if user.referred_by:
                messages.success(request, 
                    f'Compte créé avec succès! Vous avez été parrainé par {user.referred_by.username}. '
                    f'Votre code de parrainage: {user.referral_code}'
                )
            else:
                messages.success(request, 
                    f'Bienvenue {user.username}! Votre code de parrainage: {user.referral_code}'
                )
                
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    referred_users = CustomUser.objects.filter(referred_by=user)
    user_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Calculate user's rank
    users_with_more_points = CustomUser.objects.filter(points__gt=user.points).count()
    user_rank = users_with_more_points + 1
    
    # Calculate total points earned from referrals
    referral_points = referred_users.count()
    
    context = {
        'referred_users': referred_users,
        'user_orders': user_orders,
        'user_rank': user_rank,
        'referral_points': referral_points,
    }
    return render(request, 'profile.html', context)

# Add this new view for product details
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get related products (same category, excluding current product)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product_detail.html', context)


@login_required
def purchase_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock <= 0:
        messages.error(request, 'Désolé, ce produit est en rupture de stock.')
        return redirect('product_detail', product_id=product_id)
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        total_price=product.price,
        status='new'
    )
    
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price
    )
    
    # Update user points
    user = request.user
    user.points += 1
    user.save(update_fields=['points'])
    
    # Update product stock
    product.stock -= 1
    product.save(update_fields=['stock'])
    
    messages.success(request, 
        f'Commande passée avec succès! Vous avez gagné 1 point. '
        f'Total points: {user.points}'
    )
    
    return redirect('product_detail', product_id=product_id)