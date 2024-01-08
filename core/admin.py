from django.contrib import admin
from .models import Task, AdvertiseModel, Image, CityList, AdvertiseCategory, AdvertiseRating, Address, ReportAdvertise

# Register your models here.

admin.site.register(Task)


# admin.site.register(ReportAdvertise)


# admin.site.register(AdvertiseRating)


# admin.site.register(AdvertiseModel)
# admin.site.register(Address)


# admin.site.register(Image)
# admin.site.register(CityList)
# admin.site.register(AdvertiseCategory)


@admin.register(AdvertiseModel)
class AdvertiseAdmin(admin.ModelAdmin):
    list_display = ('title', 'advertise_category', 'advertise_status', 'get_town')
    search_fields = ('title', 'user__username', 'address__town')
    list_filter = ['advertise_category', 'advertise_status', 'created_at']

    def get_town(self, obj):
        return obj.address.town

    get_town.short_description = 'Town'

    # delete many adverts by admin panel
    def delete_queryset(self, request, queryset):
        for item in queryset:
            if item.address:
                item.address.delete()

        queryset.delete()


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'town', 'zip_code')
    search_fields = ('street', 'town', 'zip_code')


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_advertise_title')
    search_fields = ('title', 'advertise__title')

    def get_advertise_title(self, obj):
        return obj.advertise.title

    get_advertise_title.short_description = 'Advertise Title'


@admin.register(CityList)
class CityListAdmin(admin.ModelAdmin):
    list_display = ('city_name',)
    search_fields = ('city_name',)


@admin.register(AdvertiseCategory)
class AdvertiseCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    search_fields = ('category_name',)


@admin.register(AdvertiseRating)
class AdvertiseRatingAdmin(admin.ModelAdmin):
    list_display = ('get_advertise_title', 'short_comment', 'created_at',)
    search_fields = ('advertise__title', 'rating',)
    list_filter = ['created_at', 'rating']

    def short_comment(self, obj):
        return obj.comment[:100]

    short_comment.short_description = 'Comment'

    def get_advertise_title(self, obj):
        return obj.advertise.title

    get_advertise_title.short_description = 'Advertise Title'


@admin.register(ReportAdvertise)
class ReportAdvertise(admin.ModelAdmin):
    list_display = ('category', 'get_advertise_title', 'status', 'created_at')
    search_fields = ('advertise__title',)
    list_filter = ['category', 'status', 'created_at', ]

    def get_advertise_title(self, obj):
        return obj.advertise.title

    get_advertise_title.short_description = 'Advertise Title'
