from django import forms
from django.conf import settings
from .models import Order, Delivery
from decimal import Decimal

class OrderForm(forms.ModelForm):
    """
    Form for creating and updating orders. Includes fields for customer details,
    delivery options, and addresses, as well as VAT and total cost calculations.
    """
    vat_amount = forms.DecimalField(
        label='VAT Amount',
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control'
        })
    )
    grand_total_with_vat = forms.DecimalField(
        label='Total Amount Including VAT',
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Order
        fields = (
            'full_name', 'email', 'phone_number',
            'street_address1', 'street_address2',
            'town_or_city', 'postcode', 'country',
            'county', 'delivery_method',
        )

    def __init__(self, *args, **kwargs):
        """
        Initialise the form, adding placeholders, custom classes, and autofocus.
        """
        total_cost = kwargs.pop('total_cost', None)
        vat_amount = kwargs.pop('vat_amount', None)
        grand_total_with_vat = kwargs.pop('grand_total_with_vat', None)
        super().__init__(*args, **kwargs)

        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'country': 'Country',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County',
        }

        # Set autofocus on the first field
        self.fields['full_name'].widget.attrs['autofocus'] = True
        
        # Iterate through fields to set placeholders, classes, and labels
        for field_name, placeholder in placeholders.items():
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs['placeholder'] = placeholder
                field.widget.attrs['class'] = 'stripe-style-input'
                field.label = False
        
        # Get delivery methods
        delivery_methods = Delivery.objects.filter(active=True)
        
        # Default to Standard Delivery
        standard_delivery = delivery_methods.filter(name='Standard Delivery').first()
        free_delivery = delivery_methods.filter(name='Free Delivery').first()
        
        # Set initial delivery method based on total cost and free delivery threshold
        if total_cost and total_cost >= settings.FREE_DELIVERY_THRESHOLD and free_delivery:
            self.fields['delivery_method'].initial = free_delivery.id
            self.fields['delivery_method'].queryset = delivery_methods.filter(name='Free Delivery')
        elif standard_delivery:
            self.fields['delivery_method'].initial = standard_delivery.id
        
        # Add custom class for the delivery method dropdown
        # self.fields['delivery_method'].widget.attrs['class'] = 'stripe-style-input'
        # self.fields['delivery_method'].widget.attrs['empty_label'] = None
        
        # Set VAT amount and grand total with VAT if provided
        if vat_amount is not None:
            self.fields['vat_amount'].initial = vat_amount
        
        if grand_total_with_vat is not None:
            self.fields['grand_total_with_vat'].initial = grand_total_with_vat

#  Refrences:
#  Django Working with Forms: https://docs.djangoproject.com/en/5.1/topics/forms/#working-with-forms
#  Accept a payment using Stripe Elements: https://docs.stripe.com/payments/accept-a-payment-charges#set-up-stripe-elements
