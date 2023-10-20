from django.db import models
from django.contrib.auth.models import User

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


# without Model next migrate
class AdvertiseModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=100, null=True, blank=True)
    advertise_status = models.CharField(choices=Advertise_status, max_length=40, default='accepted')
    advertise_category = models.CharField(choices=Advertise_category, max_length=40, default='none')
    rating_sum = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    street = models.CharField(max_length=50)
    street_number = models.IntegerField(max_length=4)
    apartment_number = models.CharField(max_length=4)
    town = models.CharField(max_length=40)
    zip_code = models.CharField(max_length=6)
    updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(upload_to='images/', default='default_images/mountain.jpg', null=True, blank=True)

    def __str__(self):
        return self.title

# class Image(models.Model):
#     title = models.CharField(max_length=200)
#     image = models.ImageField(upload_to='images')
#
#     def __str__(self):
#         return self.title
#
#
# class AdvertiseImgGallery(models.Model):
#     advertise = models.ForeignKey(AdvertiseModel, related_name='advertise', on_delete=models.CASCADE)
#     gallery = models.ForeignKey(Image, on_delete=models.CASCADE)
#
#
# class ImageTags(models.Model):
#     pass
