from django import forms
from django.contrib.auth.models import User # Import Django's User model
from .models import Donor, Requester # Ensure both Donor and Requester models are imported

# Custom DateInput widget for HTML5 date picker
class DateInput(forms.DateInput):
    # Overriding the default input type to use the HTML5 date picker
    input_type = 'date'

# Form for User Registration
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the 'form-control' class to all fields
        for field_name, field in self.fields.items():
            current_attrs = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (current_attrs + ' form-control').strip()
            if field_name == 'email':
                field.widget.attrs['placeholder'] = 'e.g., user@example.com'
            elif field_name == 'username':
                field.widget.attrs['placeholder'] = 'Choose a username'
            elif field_name == 'password':
                field.widget.attrs['placeholder'] = 'Enter your password'


# Donor Registration Form
# This form is used when a new Donor account is created along with a User.
class DonorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Donor
        # We exclude 'user' because it will be set by the view after the User object is created.
        exclude = ['user'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the 'form-control' class to all fields
        for field in self.fields.values():
            current_attrs = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (current_attrs + ' form-control').strip()


# Requester Registration Form
# This form is used when a new Requester account is created along with a User.
class RequesterRegistrationForm(forms.ModelForm):
    class Meta:
        model = Requester
        # We exclude 'user' because it will be set by the view after the User object is created.
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the 'form-control' class to all fields
        for field in self.fields.values():
            current_attrs = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (current_attrs + ' form-control').strip()
            # For date fields, you can suggest a format
            if isinstance(field, forms.DateField):
                field.widget.attrs['placeholder'] = 'YYYY-MM-DD'


# Donor Form (for editing/management of Donor profiles)
class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        # Fields for the Donor profile (excluding the 'user' link, which is handled separately)
        fields = ['name', 'age', 'blood_group', 'phone', 'address']
        # Widgets from Code1 are used for DonorForm
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., MD. Hossain'}),
            'age': forms.NumberInput(attrs={'placeholder': 'e.g., 25'}),
            'phone': forms.TextInput(attrs={'placeholder': 'e.g., +8801...'}),
            'address': forms.Textarea(attrs={'placeholder': 'Enter full address', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the 'form-control' class to all fields, preserving existing attributes
        for field in self.fields.values():
            current_attrs = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (current_attrs + ' form-control').strip()


# Requester Form (for editing/management of Requester profiles or creating requests)
class RequesterForm(forms.ModelForm):
    class Meta:
        model = Requester
        # Fields are explicitly listed to ensure consistency with views and templates.
        # This list includes fields like 'date_needed', 'location', and 'message'
        # which are used for a comprehensive blood request.
        fields = ['name', 'phone', 'blood_group', 'date_needed', 'location', 'message']
        
        # Add widgets to customize form field rendering, combining from both codes
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., MD. Hossain'}),
            'phone': forms.TextInput(attrs={'placeholder': 'e.g., +8801...'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., Dhaka Medical College'}),
            'date_needed': DateInput(), # Use the custom DateInput for the 'date_needed' field
            'message': forms.Textarea(attrs={'placeholder': 'e.g., Patient needs blood for an urgent surgery.', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the 'form-control' class to all fields, preserving existing attributes
        for field in self.fields.values():
            current_attrs = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (current_attrs + ' form-control').strip()