from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views.generic import View,CreateView,TemplateView,ListView,FormView,UpdateView,DetailView
from .forms import CustomUserCreationForm,DeliveryStaffForm,ConnectionRequestForm,CylinderBookingForm,PaymentForm,UserProfileForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CustomUser,DeliveryStaff,ConnectionRequest,CylinderBooking,Payment,UserProfile
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
import razorpay
from django.core.mail import send_mail



def send_welcome_email(user):
    subject = "Welcome to Gas Booking System"
    
    # Render the HTML content from the email.html template
    message = render_to_string('email.html', {'user': user})

    # Send the email
    send_mail(
        subject,  # Subject of the email
        message,  # Plain text message (optional)
        settings.DEFAULT_FROM_EMAIL,  # Sender's email address
        [user.email],  # Recipient's email address
        fail_silently=False,
        html_message=message  # HTML content of the email
    )



class HomeView(TemplateView):
       template_name = 'home.html'

class AboutusView(TemplateView):
    template_name='aboutus.html'

class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        send_welcome_email(user)
        login(self.request, user)
        return redirect(self.success_url)

       
from django.contrib.auth.views import LoginView

class CustomLoginView(View):

    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  
            if user.is_superuser:  
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
                return render(request, 'login.html', {'form': form})


@login_required
def profile_view(request):
    user_profile = ConnectionRequest.objects.get(user=request.user,status='approved')
    return render(request, 'userprofileview.html', {'user_profile': user_profile})


@login_required
def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile_view')  
        else:
            messages.error(request, "There was an error updating your profile.")
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'edit_profile.html', {'form': form})




from django.views.generic import TemplateView

class AdminDashboardView(TemplateView):
    template_name = 'admindashboard.html'


def user_list_view(request):
    users = CustomUser.objects.all()  # Retrieve all users
    return render(request, 'userlist.html', {'users': users})

def users_list(request):
    total_users=CustomUser.objects.count()
    return render(request, 'admindashboard.html', {'total_users': total_users})


@method_decorator(staff_member_required, name='dispatch') 
class AddDeliveryStaffView(View):
    def get(self, request):
        form = DeliveryStaffForm()
        return render(request, 'add_delivery_staff.html', {'form': form})

    def post(self, request):
        form = DeliveryStaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('delivery_staff_list')  # Redirect after saving
        return render(request, 'add_delivery_staff.html', {'form': form})

class DeliveryStaffListView(ListView):
    model = DeliveryStaff
    template_name = 'delivery_staff_list.html'
    context_object_name = 'delivery_staff'



class UserDashboardView(TemplateView):
    template_name = 'customerdashboard.html'


# @login_required
class RequestConnectionView(LoginRequiredMixin,View):
    def get(self, request):
        form = ConnectionRequestForm()
        return render(request, 'request_connection.html', {'form': form})

    def post(self, request):
        form = ConnectionRequestForm(request.POST, request.FILES)
        if form.is_valid():
            connection_request = form.save(commit=False)
            connection_request.user = request.user  # Assign the logged-in user to the request
            connection_request.save()
            return redirect('user_dashboard')  # Redirect to home or another page after submission
        return render(request, 'request_connection.html', {'form': form})



class AdminRequestConnectionView(LoginRequiredMixin, ListView):
    model = ConnectionRequest
    template_name = 'admin_connection_requests.html'
    context_object_name = 'connection_requests'

    def get_queryset(self):
      
        return ConnectionRequest.objects.filter(status='pending')

    
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")


@user_passes_test(lambda u: u.is_staff) 
def admin_approve_connection(request, pk):
    connection_request = get_object_or_404(ConnectionRequest, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            connection_request.status = 'approved'
            connection_request.consumer_number = f"CON-{connection_request.id}"  # Optional: Assign a consumer number
            connection_request.save()
            return redirect('approved_requests')  # Redirect to the approved requests page

        elif action == 'deny':
            connection_request.status = 'denied'
            connection_request.save()
            return redirect('denied_requests')  # Redirect to the denied requests page

    return render(request, 'approve_deny_connection.html', {'request': connection_request})

class ApprovedRequestListView(LoginRequiredMixin, ListView):
    model = ConnectionRequest
    template_name = 'approved_requests.html'
    context_object_name = 'approved_requests'

    def get_queryset(self):
        # Show only approved requests
        return ConnectionRequest.objects.filter(status='approved')


class DeniedRequestListView(LoginRequiredMixin, ListView):
    model = ConnectionRequest
    template_name = 'denied_requests.html'
    context_object_name = 'denied_requests'

    def get_queryset(self):
        # Show only denied requests
        return ConnectionRequest.objects.filter(status='denied')




class BookCylinderView(LoginRequiredMixin, CreateView):
    model = CylinderBooking
    template_name = 'book_cylinder.html'
    fields = ['cylinder_type', 'payment_method']

    def form_valid(self, form):
        # Associate the current logged-in user with the booking
        form.instance.user = self.request.user
        
        # Get the form's cleaned data
        payment_method = form.cleaned_data['payment_method']
        cylinder_type = form.cleaned_data['cylinder_type']
        
        # Find available delivery staff
        available_staff = DeliveryStaff.objects.filter(status='available').first()

        # If available, assign the delivery staff; else, show a warning
        if available_staff:
            form.instance.delivery_staff = available_staff
            messages.success(self.request, "Booking successful! A delivery staff has been assigned.")
        else:
             messages.warning(self.request, "No delivery staff available at the moment. We'll assign staff shortly.")
        
        # Save the booking instance first
        self.object = form.save()

        # Check if the booking was successfully created and saved
        if self.object is None:
            messages.error(self.request, "There was an error with your booking. Please try again.")
            return self.form_invalid(form)

        # Calculate the total amount for the booking
        amount = self.object.calculate_amount()

        # Create a payment record with 'Pending' status
        payment = Payment.objects.create(
            user=self.request.user,
            booking=self.object,
            payment_method=payment_method,
            amount=amount,
            payment_status='Pending'
        )

        # Redirect to payment page
        return redirect('payment_page', booking_id=self.object.id)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your booking. Please try again.")
        return super().form_invalid(form)



class PaymentView(View):
    def get(self, request, booking_id):
        # Get the booking by ID
        try:
            booking = CylinderBooking.objects.get(id=booking_id)
        except CylinderBooking.DoesNotExist:
            messages.error(request, "Booking not found.")
            return redirect('booking_history')

        # Calculate the amount to be paid
        amount = booking.calculate_amount()

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create an order in Razorpay
        order = client.order.create({
            'amount': amount * 100,  # Amount in paise (multiply by 100)
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Create or update payment record
        payment, created = Payment.objects.get_or_create(
            booking=booking, payment_status='Pending',
            defaults={
                'payment_method': booking.payment_method,
                'amount': amount,
                'transaction_id': order['id'],
            }
        )

        # Prepare context for rendering payment page
        context = {
            'order_id': order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'booking_id': booking.id
        }

        return render(request, 'payment.html', context)

    def post(self, request, booking_id):

        payment_signature = request.POST.get('razorpay_signature')
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')

        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Prepare data for verification
        data={
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': payment_signature
        }

        try:
            # Verify the payment signature
            client.utility.verify_payment_signature(data)

            # Get the payment object and update status to successful
            payment = Payment.objects.get(transaction_id=order_id)
            payment.payment_status = 'Successful'
            payment.transaction_id = payment_id
            payment.save()

            # Update the booking payment status
            booking = CylinderBooking.objects.get(id=booking_id)
            booking.payment_status = True  # Set booking payment status to True
            booking.save()

            send_mail(
                'Payment Confirmation',
                f"Dear {booking.user.username}, your payment for booking ID {booking.id} was successful.",
                settings.DEFAULT_FROM_EMAIL,
                [booking.user.email],
            )


            messages.success(request, "Payment successful!")
            return redirect('booking_history')

        except Exception as e:
            messages.error(request, f"Payment verification failed: {str(e)}")
            return redirect('booking_history')


class BookingHistoryView(LoginRequiredMixin, ListView):
        model = CylinderBooking
        template_name = 'booking_history.html'
        context_object_name = 'bookings'
     
        def get_queryset(self):
            return CylinderBooking.objects.filter(user=self.request.user)
        def get_queryset(self):
            return CylinderBooking.objects.filter(user=self.request.user)
       