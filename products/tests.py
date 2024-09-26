from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError 
from decimal import Decimal
from products.models import ProductsCategory, Discount, HennaProduct


class DiscountModelTest(TestCase):
    def setUp(self):
        self.discount = Discount.objects.create(
            name='10% Off',
            discount_type='percentage',
            value=Decimal('10.00'),
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )

    def test_discount_creation(self):
        self.assertEqual(self.discount.name, '10% Off')
        self.assertEqual(self.discount.discount_type, 'percentage')
        self.assertEqual(self.discount.value, Decimal('10.00'))

    def test_discount_string_representation(self):
        self.assertEqual(str(self.discount), '10% Off (Percentage)')

    def test_discount_validation_negative_value(self):
        with self.assertRaises(ValidationError):
            discount = Discount(name='Invalid Discount', discount_type='fixed', value=Decimal('-5.00'))
            discount.clean()

    def test_discount_is_active(self):
        self.assertTrue(self.discount.is_active())
        self.discount.active = False
        self.assertFalse(self.discount.is_active())
        self.discount.active = True
        self.discount.end_date = timezone.now() - timezone.timedelta(days=1)  # Make it inactive
        self.assertFalse(self.discount.is_active())

class DiscountModelFutureDateTest(TestCase):
    def setUp(self):
        self.discount = Discount.objects.create(
            name='Future Discount',
            discount_type='percentage',
            value=Decimal('10.00'),
            start_date=timezone.now() + timezone.timedelta(days=10),  # Starts in the future
            end_date=timezone.now() + timezone.timedelta(days=20)
        )

    def test_future_discount_is_not_active(self):
        self.assertFalse(self.discount.is_active())  # Should not be active since it's in the future