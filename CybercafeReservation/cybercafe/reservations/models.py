import hashlib
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.db import models
from django.contrib.auth.models import User

class UserAccount(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10, default='customer')  # Default status set to 'customer'

    def __str__(self):
        return self.username

    def get_user(self, user_id):
        try:
            return UserAccount.objects.get(pk=user_id)
        except UserAccount.DoesNotExist:
            return None
        
# PCRental Model: Represents a rental of a PC with an hourly rate.
class PCRental(models.Model):
    pc_number = models.CharField(max_length=10)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"PC {self.pc_number} - ${self.hourly_rate}/hour"

    class Meta:
        verbose_name = "PC Rental"
        verbose_name_plural = "PC Rentals"

# PrintingOption Model: Represents available printing options such as color, black & white, etc.
class PrintingOption(models.Model):
    print_type = models.CharField(max_length=50)  # Allow custom print types
    price_per_page = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.print_type} Printing - ${self.price_per_page}/page"

    class Meta:
        verbose_name = "Printing Option"
        verbose_name_plural = "Printing Options"


# Reservation Model: Represents a reservation for either a PC rental or a printing service.
class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('UserAccount', on_delete=models.CASCADE, null=True, blank=True)

    # Reservation can be for either a PCRental or a PrintingOption
    pc_rental = models.ForeignKey('PCRental', on_delete=models.SET_NULL, null=True, blank=True)
    printing_option = models.ForeignKey('PrintingOption', on_delete=models.SET_NULL, null=True, blank=True)

    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    duration = models.PositiveIntegerField(null=True, blank=True, default=0, help_text="Duration in hours for PC rental")
    number_of_pages = models.PositiveIntegerField(null=True, blank=True, default=0, help_text="Number of pages for printing")
    file = models.FileField(upload_to='reservations/', null=True, blank=True)

    # Optional description for additional customer needs
    description = models.TextField(null=True, blank=True, help_text="Any additional needs or requests from the customer")

    payment_status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('paid', 'Paid'), ('invalid', 'Invalid')], default='pending')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        customer_name = self.customer.username if self.customer else 'Unknown'
        return f"Reservation {self.reservation_id} by {customer_name}"

    def calculate_total_price(self):
        base_price = 0
        if self.pc_rental:
            base_price = self.pc_rental.hourly_rate * self.duration
        elif self.printing_option:
            base_price = self.printing_option.price_per_page * self.number_of_pages

        # Apply discount to the base price
        self.total_price = base_price - self.discount
        return self.total_price

    def save(self, *args, **kwargs):
        # Ensure total price is calculated before saving
        self.calculate_total_price()
        super().save(*args, **kwargs)

