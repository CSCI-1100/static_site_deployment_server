from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

from django import forms

class BulkUserUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with columns: First Name, Last Name, Email, Password',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('File must be a CSV (.csv) file.')
        
        if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
            raise forms.ValidationError('File size must be under 5MB.')
        
        return csv_file

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['site_name']
        widgets = {
            'site_name': forms.TextInput(attrs={'placeholder': 'my-awesome-site'})
        }
