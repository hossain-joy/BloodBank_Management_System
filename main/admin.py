from django.contrib import admin
from .models import Profile, Donor, Requester

# Register your models here.
admin.site.register(Profile)
admin.site.register(Donor)
admin.site.register(Requester)