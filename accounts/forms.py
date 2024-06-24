from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Account, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Enter Your Password"
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Confirm Your Password"
    }))
    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number", "email", "password"]

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs["placeholder"] = "Your First Name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Your Last Name"
        self.fields["email"].widget.attrs["placeholder"] = "Your Email Address"
        self.fields["phone_number"].widget.attrs["placeholder"] = "Your Phone Number"

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Passowrd does not match"
            )


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number"]

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class ProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={"Invalid": ("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ["address_line_1", "address_line_2", "city", "state", "country", "profile_picture"]

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


