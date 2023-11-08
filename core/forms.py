from django import forms
from django.forms import ClearableFileInput

from .models import AdvertiseModel, Image, CityList


class AdvertiseForm(forms.ModelForm):
    # town = forms.ModelChoiceField(queryset=CityList.objects.all())

    class Meta:
        model = AdvertiseModel
        fields = (
            'title', 'description', 'advertise_category', 'street', 'street_number', 'apartment_number', 'town',
            'zip_code',
            'img')


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
