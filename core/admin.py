from django.contrib import admin
from .models import Task, AdvertiseModel, Image, CityList, AdvertiseCategory

# Register your models here.

admin.site.register(Task)


# admin.site.register(AdvertiseModel)
# admin.site.register(Image)
# admin.site.register(CityList)
# admin.site.register(AdvertiseCategory)


@admin.register(AdvertiseModel)
class AdvertiseAdmin(admin.ModelAdmin):
    list_display = ('title', 'advertise_category', 'advertise_status', 'town')
    search_fields = ('title', 'town', 'user__username')
    list_filter = ['advertise_category', 'advertise_status', ]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title', 'advertise__title')


@admin.register(CityList)
class CityListAdmin(admin.ModelAdmin):
    list_display = ('city_name',)
    search_fields = ('city_name',)


@admin.register(AdvertiseCategory)
class AdvertiseCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    search_fields = ('category_name',)
