from django import forms
from .models import AdvertiseModel


class AdvertiseForm(forms.ModelForm):
    class Meta:
        model = AdvertiseModel
        fields = ('user',
                  'title', 'description', 'advertise_category', 'street', 'street_number', 'apartment_number', 'town',
                  'zip_code',
                  'img')
