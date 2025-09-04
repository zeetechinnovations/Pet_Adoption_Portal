from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    mobile_number = forms.CharField(max_length=15, required=True, help_text="Required. Enter a valid mobile number (e.g., +1234567890).")

    class Meta:
        model = User
        fields = ['username', 'email', 'mobile_number', 'password1', 'password2']

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if not mobile_number.replace('+', '').replace('-', '').isdigit():
            raise forms.ValidationError("Mobile number must contain only digits, +, or -.")
        if len(mobile_number) < 10 or len(mobile_number) > 15:
            raise forms.ValidationError("Mobile number must be between 10 and 15 characters.")
        return mobile_number