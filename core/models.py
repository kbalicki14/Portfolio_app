from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

Advertise_status = (
    ('pending', 'Wait for review'),  # oczekujący na dodanie
    ('accepted', 'Accepted'),
    ('deleted', 'Deleted'),
    ('suspend', 'Temporary suspended'),  # zawieszony
)

Advertise_category = (
    ('none', 'none'),
    ('hairdress', 'Hairdress'),
    ('barber', 'Barber Shop'),
    ('tatto', 'Tatto Studio'),
    ('cosmetic', 'Cosmetic'),
)


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['complete']


class AdvertiseCategory(models.Model):
    category_name = models.CharField(max_length=40)

    def __str__(self):
        return self.category_name


# without Model next migrate
class AdvertiseModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=60)
    description = models.TextField(max_length=200, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    advertise_status = models.CharField(choices=Advertise_status, max_length=40, default='accepted')
    advertise_category = models.ForeignKey(AdvertiseCategory, on_delete=models.CASCADE)
    street = models.CharField(max_length=50)
    street_number = models.CharField(max_length=4)
    apartment_number = models.CharField(max_length=4)
    town = models.CharField(max_length=40)
    zip_code = models.CharField(max_length=6)
    updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(upload_to='images/', default='default_images/mountain.jpg', null=True, blank=True)

    def __str__(self):
        return self.title


class Image(models.Model):
    title = models.CharField(max_length=50, default='No title')
    image = models.ImageField(upload_to='images/gallery/')
    advertise = models.ForeignKey(AdvertiseModel, related_name='advertise', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# commnet null
class AdvertiseRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    advertise = models.ForeignKey(AdvertiseModel, on_delete=models.CASCADE)
    rating = models.FloatField(default=0.0)
    comment = models.TextField(max_length=450)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment


class CityList(models.Model):
    city_name = models.CharField(max_length=100)

    def __str__(self):
        return self.city_name

# class Address(models.Model):
#     pass

# class ImageGallery(models.Model):
#     advertise = models.ForeignKey(AdvertiseModel, related_name='advertise', on_delete=models.CASCADE)
#     # gallery = models.ForeignKey(Image, on_delete=models.CASCADE)

# class ImageTags(models.Model):
#     pass
