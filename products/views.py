from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils import timezone
from .models import HennaProduct, ProductsCategory

def all_products(request):
    """A view to show all products, including sorting and search queries."""

    products = HennaProduct.objects.all()
    query = None
    categories = None
    sort = None
    direction = None
    discounted = request.GET.get('discounted') == 'true'

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)
            
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = ProductsCategory.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

        # Filter by discounted items  Ref: https://docs.djangoproject.com/en/5.1/topics/db/queries/#field-lookups
        if discounted:
            products = products.filter(
                discounts__active=True,
                discounts__start_date__lte=timezone.now(),
                discounts__end_date__gte=timezone.now()
            ).distinct()

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """A view to show individual product details, including discounted price and discount name."""

    product = get_object_or_404(HennaProduct, pk=product_id)
    discounted_price = product.get_discounted_price()

    # Get the currently active discount
    discount_name = None
    current_discount = product.get_current_discount()
    if current_discount:
        discount_name = current_discount.name

    context = {
        'product': product,
        'discounted_price': discounted_price,
        'discount_name': discount_name,
    }

    return render(request, 'products/product_detail.html', context)
