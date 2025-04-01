"""
URL configuration for OGBS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from booking import views
from booking.views import user_list_view
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/',admin.site.urls),
    path('',views.HomeView.as_view(), name='home'),
    path('register/',views.RegisterView.as_view(), name='register'),
    path('login/',views.CustomLoginView.as_view(), name='login'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('aboutus/',views.AboutusView.as_view(),name='aboutus'),
    path('user-list/', user_list_view, name='user_list'),
    path('admin-dashboard/',views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('add-delivery-staff/',views.AddDeliveryStaffView.as_view(), name='add_delivery_staff'),
    path('delivery-staff-list/',views.DeliveryStaffListView.as_view(), name='delivery_staff_list'),
    path('delivery-staff-edit/<int:pk>/',views.DeliveryStaffEditView.as_view(), name='delivery_staff_edit'),

    path('user-dashboard/',views.UserDashboardView.as_view(), name='user_dashboard'),
    path('request-connection/',views.RequestConnectionView.as_view(), name='request_connection'),
    path('admins/connection-requests/',views.AdminRequestConnectionView.as_view(), name='admin_connection_requests'),
    path('admins/connection-request/<int:pk>/',views.AdminRequestConnectionView.as_view(), name='admin_connection_request_manage'),
    path('admins/connection-requests/approve/<int:pk>/', views.admin_approve_connection, name='admin_approve_connection'),
    path('admins/connection-requests/approved/', views.ApprovedRequestListView.as_view(), name='approved_requests'),
    path('admins/connection-requests/denied/', views.DeniedRequestListView.as_view(), name='denied_requests'),
    path('book-cylinder/', views.BookCylinderView.as_view(), name='book_cylinder'),
    path('booking-history/', views.BookingHistoryView.as_view(), name='booking_history'),
    path('payment/<int:booking_id>/', views.PaymentView.as_view(), name='payment_page'),
    path('bookings/',views.AdminBookingListView.as_view(), name='admin_bookings'),
    path('admin-dashboard/', views.users_list, name='admin_dashboard'),
    path('payments/',views.PaymentHistoryView.as_view(), name='payment_history'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="password_reset.html"), name="password_reset"),
    
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="password_reset_done.html"), name="password_reset_done"),
    
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="password_reset_confirm.html"), name="password_reset_confirm"),
    
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="password_reset_complete.html"), name="password_reset_complete"),



    
]
if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

