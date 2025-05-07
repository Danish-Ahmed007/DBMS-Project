from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """Custom form for user registration that includes the location field."""
    first_name = forms.CharField(max_length=30, required=True, help_text="Required. Enter your first name.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required. Enter your last name.")
    location = forms.CharField(max_length=100, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'location', 'password1', 'password2']
        
class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form for login."""
    class Meta:
        model = CustomUser