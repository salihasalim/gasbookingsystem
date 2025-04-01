from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import login,logout
from django.views.generic import View,CreateView,TemplateView,ListView,FormView,UpdateView,DetailView
from .forms import CustomUserCreationForm,DeliveryStaffForm,ConnectionRequestForm,CylinderBookingForm,PaymentForm,UserProfileForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CustomUser,DeliveryStaff,ConnectionRequest,CylinderBooking,Payment,UserProfile
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.views.decorators.cache import never_cache
from booking.decorators import signin_required
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
import razorpay
from django.core.mail import send_mail
from django.utils import timezone  # Import timezone
from datetime import timedelta
import random



def send_welcome_email(user):
    subject = "Welcome to Gas Booking System"
    
    message = render_to_string('email.html', {'user': user})

    send_mail(
        subject, 
        message, 
        settings.DEFAULT_FROM_EMAIL,  
        [user.email],  
        fail_silently=False,
        html_message=message 
    )

@method_decorator(never_cache, name='dispatch')
class HomeView(TemplateView):
       template_name = 'home.html'
@method_decorator(never_cache, name='dispatch')
class AboutusView(TemplateView):
    template_name='aboutus.html'
@method_decorator(never_cache, name='dispatch')
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

@method_decorator(never_cache, name='dispatch')

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

        # If the form is invalid, show an error message
        messages.error(request, "Invalid username or password. Please try again.")
        return render(request, 'login.html', {'form': form})  # Ensure response is returned




@never_cache
def profile_view(request):
    connection_request = ConnectionRequest.objects.filter(user=request.user).first()  # Avoids .get() error
    return render(request, 'userprofileview.html', {'connection_request': connection_request})



@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get the latest connection request or create a new one
    connection_request = ConnectionRequest.objects.filter(user=request.user).order_by('-requested_at').first()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        connection_form = ConnectionRequestForm(request.POST, request.FILES, instance=connection_request)
        
        if form.is_valid() and connection_form.is_valid():
            form.save()
            connection_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile_view')  
        else:
            messages.error(request, "There was an error updating your profile.")
    
    else:
        form = UserProfileForm(instance=user_profile)
        connection_form = ConnectionRequestForm(instance=connection_request)

    return render(request, 'edit_profile.html', {'form': form, 'connection_form': connection_form})

decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
class AdminDashboardView(TemplateView):
    template_name = 'admindashboard.html'

    total_users = CustomUser.objects.count()

    

    new_bookings = CylinderBooking.objects.filter(booking_date__gte=timezone.now() - timedelta(days=10)).count()

    
    total_revenue = sum(payment.amount for payment in Payment.objects.all())



@never_cache
def user_list_view(request):
    users = CustomUser.objects.all()  
    return render(request, 'userlist.html', {'users': users})

@never_cache
def users_list(request):
    total_users=CustomUser.objects.count()
    return render(request, 'admindashboard.html', {'total_users': total_users})

@method_decorator(never_cache, name='dispatch')
@method_decorator(staff_member_required, name='dispatch') 
class AddDeliveryStaffView(View):
    def get(self, request):
        form = DeliveryStaffForm()
        return render(request, 'add_delivery_staff.html', {'form': form})

    def post(self, request):
        form = DeliveryStaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('delivery_staff_list')  
        return render(request, 'add_delivery_staff.html', {'form': form})
@method_decorator(never_cache, name='dispatch')
class DeliveryStaffListView(ListView):
    model = DeliveryStaff
    template_name = 'delivery_staff_list.html'
    context_object_name = 'delivery_staff'

@method_decorator(never_cache, name='dispatch')
class DeliveryStaffEditView(View):
    def get(self, request, pk):
        delivery_staff = get_object_or_404(DeliveryStaff, pk=pk)
        form = DeliveryStaffForm(instance=delivery_staff)
        return render(request, 'delivery_staff_edit.html', {'form': form, 'delivery_staff': delivery_staff})

    def post(self, request, pk):
        delivery_staff = get_object_or_404(DeliveryStaff, pk=pk)
        form = DeliveryStaffForm(request.POST, instance=delivery_staff)
        if form.is_valid():
            form.save()
            return redirect('delivery_staff_list')  
        return render(request, 'delivery_staff_edit.html', {'form': form, 'delivery_staff': delivery_staff})

@method_decorator(decs,name="dispatch")
class UserDashboardView(TemplateView):
    template_name = 'customerdashboard.html'

@method_decorator(never_cache, name='dispatch')

class RequestConnectionView(LoginRequiredMixin, View):
    def get(self, request):
        form = ConnectionRequestForm()
        return render(request, 'request_connection.html', {'form': form})

    def post(self, request):
        # Check if the user has an existing connection request or an active connection
        existing_request = ConnectionRequest.objects.filter(user=request.user, status__in=['pending', 'approved']).exists()

        if existing_request:
            messages.error(request, "You have already applied for a connection or have an existing connection. "
                                    "Please contact our office if you have any concerns.")
            return redirect('user_dashboard')  # Redirecting to user dashboard or another appropriate page

        form = ConnectionRequestForm(request.POST, request.FILES)
        if form.is_valid():
            connection_request = form.save(commit=False)
            connection_request.user = request.user  
            connection_request.save()
            messages.success(request, "Your connection request has been submitted successfully.")
            return redirect('user_dashboard')  

        return render(request, 'request_connection.html', {'form': form})


@method_decorator(decs,name="dispatch")
class AdminRequestConnectionView(LoginRequiredMixin, ListView):
    model = ConnectionRequest
    template_name = 'admin_connection_requests.html'
    context_object_name = 'connection_requests'

    def get_queryset(self):
      
        return ConnectionRequest.objects.filter(status='pending')

    
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")


def generate_unique_consumer_number():
    """Generate a 12-digit unique consumer number."""
    while True:
        new_number = str(random.randint(100000000000, 999999999999))
        if not ConnectionRequest.objects.filter(consumer_number=new_number).exists():
            return new_number


@never_cache
@user_passes_test(lambda u: u.is_staff) 
def admin_approve_connection(request, pk):
    connection_request = get_object_or_404(ConnectionRequest, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            connection_request.status = 'approved'
            
            # Assign a new 12-digit consumer number
            connection_request.consumer_number = generate_unique_consumer_number()
            
            connection_request.save()
            subject = "Gas Connection Approved ✅"
            message = f"""
            Dear {connection_request.user.first_name},

            Congratulations! Your gas connection request has been approved.
            
            Your Consumer Number: {connection_request.consumer_number}
            
            You can now book cylinders through our platform.

            Regards,
            GasConnect Team
            """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [connection_request.user.email])

            messages.success(request, "Connection request approved, and email sent to the user!")
            return redirect('approved_requests')
            

        elif action == 'deny':
            connection_request.status = 'denied'
            connection_request.save()
            messages.error(request, "❌ Connection request denied.")
            return redirect('denied_requests')


    return render(request, 'approve_deny_connection.html', {'request': connection_request})




# def admin_approve_connection(request, pk):
#     connection_request = get_object_or_404(ConnectionRequest, pk=pk)

#     if request.method == 'POST':
#         action = request.POST.get('action')

#         if action == 'approve':
#             connection_request.status = 'approved'
#             connection_request.consumer_number = f"CON-{connection_request.id}"  
#             connection_request.save()
#             return redirect('approved_requests') 
#         elif action == 'deny':
#             connection_request.status = 'denied'
#             connection_request.save()
#             return redirect('denied_requests')  

#     return render(request, 'approve_deny_connection.html', {'request': connection_request})

@method_decorator(decs,name="dispatch")
class ApprovedRequestListView(LoginRequiredMixin, ListView):
    model = ConnectionRequest
    template_name = 'approved_requests.html'
    context_object_name = 'approved_requests'

    def get_queryset(self):

        return ConnectionRequest.objects.filter(status='approved')

@method_decorator(decs,name="dispatch")
class DeniedRequestListView(LoginRequiredMixin, ListView):
    model = ConnectionRequest
    template_name = 'denied_requests.html'
    context_object_name = 'denied_requests'

    def get_queryset(self):

        return ConnectionRequest.objects.filter(status='denied')



@method_decorator(decs,name="dispatch")
class BookCylinderView(LoginRequiredMixin, CreateView):
    model = CylinderBooking
    template_name = 'book_cylinder.html'
    fields = ['cylinder_type', 'payment_method']

    def form_valid(self, form):
        user = self.request.user

        connection = ConnectionRequest.objects.filter(user=user, status='approved').exists()
        if not connection:
            messages.error(self.request, "You cannot book a cylinder without an approved connection. Please contact our office.")
            return redirect('user_dashboard')

        current_year = now().year
        yearly_booking_count = CylinderBooking.objects.filter(user=user, booking_date__year=current_year).count()
        if yearly_booking_count >= 12:
            messages.error(self.request, "You have reached the maximum limit of 12 cylinders per year. You cannot book more at this time.")
            return redirect('booking_history')

        form.instance.user = user
        available_staff = DeliveryStaff.objects.filter(status='available').first()
        if available_staff:
            form.instance.delivery_staff = available_staff
            messages.success(self.request, "Booking successful! A delivery staff has been assigned.")
        else:
            messages.warning(self.request, "No delivery staff available at the moment. We will assign one shortly.")

        self.object = form.save()

        amount = self.object.calculate_amount()
        payment_method = form.cleaned_data['payment_method']

        payment = Payment.objects.create(
            user=user,
            booking=self.object,
            payment_method=payment_method,
            amount=amount,
            payment_status='Pending'
        )

        # ✅ Step 5: Redirect based on payment method
        if payment_method in ['UPI', 'Credit Card']:
            return redirect('payment_page', booking_id=self.object.id)
        else:
            payment.payment_status = 'COD Pending'
            payment.save()
            messages.success(self.request, "Booking successful! Payment will be collected on delivery.")
            return redirect('booking_history')

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your booking. Please try again.")
        return super().form_invalid(form)

@method_decorator(decs,name="dispatch")
@method_decorator(csrf_exempt, name='dispatch')
class PaymentView(View):
    def get(self, request, booking_id):
        try:
            booking = CylinderBooking.objects.get(id=booking_id)
        except CylinderBooking.DoesNotExist:
            messages.error(request, "Booking not found.")
            return redirect('booking_history')

        if booking.payment_method == 'cash_on_delivery':
            messages.error(request, "Invalid payment method for online payment.")
            return redirect('booking_history')

        amount = booking.calculate_amount()

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        order = client.order.create({
            'amount': amount * 100,  
            'currency': 'INR',
            'payment_capture': '1'
        })

        payment = Payment.objects.get(booking=booking, payment_status='Pending')
        payment.transaction_id = order['id']
        payment.save()

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

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        data = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': payment_signature
        }

        try:
            client.utility.verify_payment_signature(data)

            payment = Payment.objects.get(transaction_id=order_id)
            payment.payment_status = 'Successful'
            payment.transaction_id = payment_id  
            payment.save()

            booking = CylinderBooking.objects.get(id=booking_id)
            booking.payment_status = True  
            booking.save()

            send_mail(
                'Payment Confirmation',
                f"Dear {booking.user.username}  your payment for booking ID {booking.id}  on online gas booking systemwas successful.",
                settings.DEFAULT_FROM_EMAIL,
                [booking.user.email],
            )

            messages.success(request, "Payment successful!")
            return redirect('booking_history')

        except Exception as e:
            messages.error(request, f"Payment verification failed: {str(e)}")
            return redirect('booking_history')


@method_decorator(decs,name="dispatch")
class BookingHistoryView(LoginRequiredMixin, ListView):
    model = CylinderBooking
    template_name = 'booking_history.html'
    context_object_name = 'bookings'
 
    def get_queryset(self):
        return CylinderBooking.objects.filter(user=self.request.user)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookings = context['bookings']
        for booking in bookings:
            try:
                booking.payment_info = Payment.objects.get(booking=booking)
            except Payment.DoesNotExist:
                booking.payment_info = None
        return context

@method_decorator(decs,name="dispatch")
class AdminBookingListView(ListView):
    model = CylinderBooking
    template_name = 'booking_list.html'  # Create this template
    context_object_name = 'bookings'
    ordering = ['-booking_date'] 

class LogoutView(View):
    def get(self,request,*args,**kwargs):
        
        logout(request)
    
        return redirect('home') 

@method_decorator(decs,name="dispatch")
class PaymentHistoryView(ListView):
    model = Payment
    template_name = 'payment_history.html'
    context_object_name = 'payments'
    ordering = ['-payment_date']