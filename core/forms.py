from django import forms
from django.forms import ClearableFileInput
from phonenumber_field.formfields import PhoneNumberField
from .models import AdvertiseModel, Image, CityList, AdvertiseRating, Address


class AdvertiseForm(forms.ModelForm):
    # town = forms.ModelChoiceField(queryset=CityList.objects.all())
    phone_number = PhoneNumberField(region="PL")

    class Meta:
        model = AdvertiseModel
        fields = (
            'title', 'description', 'phone_number', 'advertise_category', 'img')


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('street', 'street_number', 'apartment_number', 'town', 'zip_code',)


class RatingForm(forms.ModelForm):
    rating = forms.FloatField(max_value=5.0, min_value=1.0)

    class Meta:
        model = AdvertiseRating
        fields = ['rating', 'comment']


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'image', 'advertise']

    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        self.fields['advertise'].required = False


class MultiImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image', widget=forms.ClearableFileInput(attrs={"multiple": True}))

    class Meta:
        model = Image
        fields = ['title', 'image', 'advertise']
