from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,UserProfile,DeliveryStaff,ConnectionRequest,DeliveryStaff,CylinderBooking,Payment

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = ConnectionRequest
        fields = ['address','phone','aadhaar_card','ration_card','photo','consumer_number']  # Add any fields that you want to be editable.
        widgets = {
            'address': forms.Textarea(attrs={'cols': 40, 'rows': 3}),
        }




class DeliveryStaffForm(forms.ModelForm):
    class Meta:
        model = DeliveryStaff
        fields = ['name', 'phone', 'email', 'status']

        widgets = {
            'status': forms.Select(choices=DeliveryStaff.STATUS_CHOICES)
        }



class ConnectionRequestForm(forms.ModelForm):
    class Meta:
        model = ConnectionRequest
        fields = ['address', 'phone', 'aadhaar_card', 'ration_card', 'photo']


class CylinderBookingForm(forms.ModelForm):
    class Meta:
        model = CylinderBooking
        fields = ['cylinder_type', 'payment_method']


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'transaction_id']

