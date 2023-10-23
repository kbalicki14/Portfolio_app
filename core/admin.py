from django.contrib import admin
from .models import Task, AdvertiseModel, Image

# Register your models here.

admin.site.register(Task)
admin.site.register(AdvertiseModel)
admin.site.register(Image)
