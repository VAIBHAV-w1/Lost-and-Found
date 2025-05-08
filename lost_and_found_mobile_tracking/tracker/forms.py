# tracker/forms.py
from django import forms
from .models import MobileReport

class MobileReportForm(forms.ModelForm):
    class Meta:
        model = MobileReport
        fields = ['brand', 'model', 'imei', 'color', 'status', 'location', 'contact_info', 'photo']
