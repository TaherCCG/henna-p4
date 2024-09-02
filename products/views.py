from django.shortcuts import render, get_object_or_404
from .models import HennaProduct

def all_products(request):
    """A view to show all products, including sorting and search queries."""

    # Get query parameters for sorting and searching
    sort_by = request.GET.get('sort', 'name')
    search_query = request.GET.get('search', '')

    # Filter and sort products
    products = HennaProduct.objects.filter(name__icontains=search_query).order_by(sort_by)

    # Context dictionary with sorting and search query
    context = {
        'products': products,
        'search_query': search_query,
        'sort_by': sort_by,
    }

    return render(request, 'products/products.html', context)

def product_detail(request, product_id):
    """A view to show individual product details."""

    product = get_object_or_404(HennaProduct, pk=product_id)

    # Context dictionary for the product detail
    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)