from django import forms
from .models import Order, Delivery

class OrderForm(forms.ModelForm):
    """
    Form for creating and updating orders. Includes fields for customer details,
    delivery options, and addresses.
    """
    
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
                field.widget.attrs['class'] = 'form-control' 
                field.label = False
        
        # Custom styling for the delivery method field
        self.fields['delivery_method'].widget.attrs['class'] = 'form-select'