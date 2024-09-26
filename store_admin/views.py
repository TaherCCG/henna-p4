from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from profiles.models import UserProfile
from checkout.models import Order

@staff_member_required
def dashboard(request):
    print("Dashboard view accessed")
    return render(request, 'store_admin/dashboard.html')

@staff_member_required
def manage_products(request):
    """Displays the product management interface."""
    return render(request, 'store_admin/manage_products.html')

@staff_member_required
def manage_discounts(request):
    """Displays the discount management interface."""
    return render(request, 'store_admin/manage_discounts.html')

@staff_member_required
def manage_delivery(request):
    """Displays the delivery management interface."""
    return render(request, 'store_admin/manage_delivery.html')

@staff_member_required
def manage_orders(request):
    """Displays the order management interface."""
    return render(request, 'store_admin/manage_orders.html')

@staff_member_required
def manage_users(request):
    """Displays a list of all users with their last login."""
    users = User.objects.all().order_by('-last_login')
    return render(request, 'store_admin/manage_users.html', {'users': users})

@staff_member_required
def user_detail(request, user_id):
    """Displays detailed information about a user, including their order history."""
    user = get_object_or_404(User, pk=user_id)
    profile = get_object_or_404(UserProfile, user=user)
    orders = Order.objects.filter(user_profile=profile)

    return render(request, 'store_admin/user_detail.html', {
        'user': user,
        'profile': profile,
        'orders': orders
    })