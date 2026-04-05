import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import ItemReport

class CustomUserCreationForm(UserCreationForm):
    """Extended signup form to capture universally required validation parameters."""
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False, help_text="Used to receive contact updates (e.g. +91 9988776655)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_phone_number(self) -> str:
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Strip spaces, dashes, and parentheses for basic validation
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not re.match(r'^\+?[1-9]\d{6,14}$', cleaned_phone):
                raise ValidationError("Please provide a valid phone number (up to 15 digits).")
            return cleaned_phone
        return ""

class ItemReportForm(forms.ModelForm):
    """Standard form for handling Lost and Found submissions tied strictly to the model constraints."""
    location_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'id_location_name', 'readonly': 'readonly', 'placeholder': 'Click on the map to firmly pin a location'}))
    latitude = forms.FloatField(widget=forms.HiddenInput(attrs={'id': 'id_latitude'}), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(attrs={'id': 'id_longitude'}), required=False)
    item_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    class Meta:
        model = ItemReport
        fields = ['report_type', 'category', 'title', 'description', 'location_name', 'latitude', 'longitude', 'item_date', 'contact_info', 'photo']
