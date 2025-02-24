from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,UserProfile,DeliveryStaff,Delivery,ConnectionRequest

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(UserProfile)


class DeliveryStaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name', 'phone', 'email')

admin.site.register(DeliveryStaff, DeliveryStaffAdmin)

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'gas_type', 'quantity', 'order_status', 'delivery_staff')
    search_fields = ('customer__username', 'gas_type','order_status')

    list_filter = ('order_status', 'gas_type')

admin.site.register(Delivery,DeliveryAdmin)



class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'consumer_number', 'requested_at', 'address', 'phone')
    search_fields = ('user__username', 'status', 'consumer_number', 'address')
    list_filter = ('status',)

admin.site.register(ConnectionRequest, ConnectionRequestAdmin)
