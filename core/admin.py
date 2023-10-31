from django.contrib import admin
from .models import Task, AdvertiseModel, Image, CityList

# Register your models here.

admin.site.register(Task)
admin.site.register(AdvertiseModel)
admin.site.register(Image)
admin.site.register(CityList)
