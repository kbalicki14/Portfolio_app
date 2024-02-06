import os
import uuid

from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

from django.core.files import File
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from datetime import datetime
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Create your models here.

Advertise_status = (
    ('pending', 'Wait for review'),  # oczekujący na dodanie
    ('accepted', 'Accepted'),
    ('deleted', 'Deleted'),
    ('suspend', 'Temporary suspended'),  # zawieszony
)
Report_status = (
    ('pending', 'Wait for review'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('deleted', 'Deleted'),
)
Advertise_category = (
    ('none', 'none'),
    ('hairdress', 'Hairdress'),
    ('barber', 'Barber Shop'),
    ('tatto', 'Tatto Studio'),
    ('cosmetic', 'Cosmetic'),
)
Report_category = (
    ('scam', 'Scam'),
    ('impersonation', 'Impersonation'),
    ('false_information', 'False information'),
    ('copyright', 'Copyright'),
    ('spam', 'Spam'),
    ('other', 'Other'),

)


class AdvertiseCategory(models.Model):
    category_name = models.CharField(max_length=40)

    def __str__(self):
        return self.category_name


def image_compression(image):
    pil_image = PilImage.open(image)
    output_io = BytesIO()
    pil_image.save(output_io, 'JPEG', quality=60)
    new_image = File(output_io, name=image.name)
    return new_image


def custom_image_compress(image_file):
    with PilImage.open(image_file) as img:
        if img.width > 1350 or img.height > 1080:
            new_resolution = (1350, 1080)
            img.thumbnail(new_resolution)
            
        if img.mode != 'RGB':
            img = img.convert('RGB')

        img_io = BytesIO()
        # replace name to uuid|
        ext = 'jpeg'
        filename = "%s.%s" % (uuid.uuid4(), ext)
        # image_file = ContentFile(img_io.getvalue(), filename)
        img.save(img_io, quality=60, format='JPEG')
        image_file = InMemoryUploadedFile(img_io, 'ImageField', filename, 'image/jpeg', img_io.tell(), None)

    return image_file


# apartment_number null
class Address(models.Model):
    street = models.CharField(max_length=50)
    street_number = models.CharField(max_length=4)
    apartment_number = models.CharField(max_length=4, null=True, blank=True)
    town = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s" % (self.street, self.street_number, self.town)


# without Model next migrate
class AdvertiseModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=60)
    description = models.TextField(max_length=600, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    advertise_status = models.CharField(choices=Advertise_status, max_length=40, default='accepted')
    advertise_category = models.ForeignKey(AdvertiseCategory, on_delete=models.CASCADE)
    address = models.OneToOneField(Address, related_name='address', on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images', default='default_images/mountain.jpg', null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # issue save 2 times
        if self.image:
            self.image = custom_image_compress(self.image)
        super().save(*args, **kwargs)


class Image(models.Model):
    title = models.CharField(max_length=50, default='No title')
    image = models.ImageField(upload_to='images')
    advertise = models.ForeignKey(AdvertiseModel, related_name='advertise', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.image = custom_image_compress(self.image)
        super().save(*args, **kwargs)


class AdvertiseRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    advertise = models.ForeignKey(AdvertiseModel, on_delete=models.CASCADE)
    rating = models.FloatField(default=0.0)
    comment = models.TextField(max_length=450, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment


class CityList(models.Model):
    city_name = models.CharField(max_length=100)

    def __str__(self):
        return self.city_name


class ReportAdvertise(models.Model):
    email = models.EmailField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(choices=Report_category, max_length=50, default='other')
    message = models.TextField(max_length=300)
    advertise = models.ForeignKey(AdvertiseModel, on_delete=models.CASCADE)
    status = models.CharField(choices=Report_status, max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message

# class Task(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     title = models.CharField(max_length=50, null=True, blank=True)
#     description = models.TextField(null=True, blank=True)
#     complete = models.BooleanField(default=False)
#     create = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         ordering = ['complete']

# @receiver(post_delete, sender=AdvertiseModel)
# def delete_related_address(sender, instance, **kwargs):
#     if instance.address:
#         instance.address.delete()

# class ImageGallery(models.Model):
#     advertise = models.ForeignKey(AdvertiseModel, related_name='advertise', on_delete=models.CASCADE)
#     # gallery = models.ForeignKey(Image, on_delete=models.CASCADE)

# class ImageTags(models.Model):
#     pass
