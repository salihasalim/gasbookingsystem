from django.apps import AppConfig


class BookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking'



class BookingConfig(AppConfig):
       name = 'booking'

       def ready(self):
           import booking.signals