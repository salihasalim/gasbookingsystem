from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from django.utils import timezone



# def generate_consumer_number():
#     # You can implement a more complex logic to generate a unique consumer number.
#     # For now, we'll generate a random number with a combination of letters and digits.
#     consumer_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
#     return consumer_number

class CustomUser(AbstractUser):
    phone = models.IntegerField(null=True, blank=True,unique=True)
    
    def str(self):
        return self.username



class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(max_length=255, null=True, blank=True)  # Example additional field
    adhar_number = models.IntegerField(unique=True,null=True,blank=True)  

def __str__(self):
    return f'{self.user.username} Profile' 

class ConnectionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # The user requesting the connection
    address = models.CharField(max_length=255)  # Address for connection
    phone = models.CharField(max_length=15)  # Contact number
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Request status
    consumer_number = models.CharField(max_length=20, blank=True, null=True)  # Automatically generated consumer number
    rejection_reason = models.TextField(null=True, blank=True)  # Reason for rejection if rejected
    requested_at = models.DateTimeField(default=timezone.now)
    aadhaar_card = models.FileField(upload_to='documents/aadhaar/', null=True, blank=True)
    ration_card = models.FileField(upload_to='documents/ration/', null=True, blank=True)
    photo = models.ImageField(upload_to='documents/photos/', null=True, blank=True)
    def str(self):
        return f"Connection Request by {self.user.username}"

    def save(self, *args, **kwargs):
        # If the request is approved, automatically generate a consumer number
        if self.status == 'approved' and not self.consumer_number:
            self.consumer_number = f"CONSUMER-{self.user.id}-{self.requested_at.strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

  
def generate_consumer_number(self):
        """Automatically generate a unique consumer number"""
        if not self.consumer_number:
            # For example, generate a random consumer number or use a simple auto-incrementing method
            self.consumer_number = f'CON{self.id:04d}'  # Format like 'CON0001', 'CON0002', etc.
            self.save()

def str(self):
        return f"Request by {self.user.username} - {self.status}"


   

class DeliveryStaff(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('in_delivery', 'In Delivery'),
        ('available', 'Available')
    ]

    name = models.CharField(max_length=255)
    phone = models.IntegerField()
    email = models.EmailField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='inactive')

    def str(self):
        return self.name



class Delivery(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link to the customer (User)
    delivery_address = models.CharField(max_length=255)
    delivery_date = models.DateTimeField()
    gas_type = models.CharField(max_length=50)  # Type of gas (LPG, Commercial, etc.)
    quantity = models.PositiveIntegerField()  # Quantity of gas
    order_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('dispatched', 'Dispatched'), ('delivered', 'Delivered')], default='pending')
    delivery_staff = models.ForeignKey(DeliveryStaff, null=True, blank=True, on_delete=models.SET_NULL)  # Delivery staff assigned to this order

    def str(self):
        return f"Order {self.id} - {self.customer.username}"
    




   
class CylinderBooking(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('CreditCard', 'Credit Card'),
        ('COD', 'Cash on Delivery')
    ]
    CYLINDER_TYPE_CHOICE=[
        ('Domestic','Domestic'),
        ('commercial','Commercial')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cylinder_type = models.CharField(max_length=20,choices=CYLINDER_TYPE_CHOICE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.BooleanField(default=False) 
    booking_date = models.DateTimeField(auto_now_add=True
    )
    delivery_staff = models.ForeignKey(DeliveryStaff, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Booking of {self.cylinder_type} by {self.user.username}"

    def calculate_amount(self):
        base_amount = 0
        if self.cylinder_type == 'Domestic':
            base_amount = 850
        elif self.cylinder_type == 'Commercial':
            base_amount = 1100

        # Add delivery charge
        delivery_charge = 50
        total_amount = base_amount + delivery_charge

        return total_amount





class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('Debit Card', 'Debit Card'),
        ('Credit Card', 'Credit Card'),
        ('COD', 'Cash on Delivery')
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Successful', 'Successful'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    booking = models.ForeignKey(CylinderBooking, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Payment for {self.booking} - {self.payment_status}"

