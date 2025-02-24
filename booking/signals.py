from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile,Delivery,DeliveryStaff

   # Signal to create a user profile after the CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
       if created:  # Only create the profile when the user is first created
           print(f"User {instance.username} created, creating profile...")
           UserProfile.objects.create(user=instance)  # Create profile for the new user

   # Signal to save the user profile after the CustomUser is saved
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
       if hasattr(instance, 'profile'):
           instance.profile.save()  


@receiver(pre_save, sender=Delivery)
def update_delivery_staff_status(sender, instance, **kwargs):
    if instance.delivery_staff:
        # If the delivery staff is assigned, set their status to 'in_delivery'
        instance.delivery_staff.status = 'in_delivery'
        instance.delivery_staff.save()



@receiver(post_save, sender=Delivery)
def reset_delivery_staff_status(sender, instance, **kwargs):
    if instance.status == 'delivered' and instance.delivery_staff:
        # Once the delivery is delivered, mark the delivery staff as available
        instance.delivery_staff.status = 'available'
        instance.delivery_staff.save()




