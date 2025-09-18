from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Event, Photo

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["first_name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "First Name (optional)"}
        )
        self.fields["last_name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Last Name (optional)"}
        )
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})


class EventForm(forms.ModelForm):
    """Form for creating and editing events"""

    class Meta:
        model = Event
        fields = ["name"]

    def save(self, commit=True, user=None):
        event = super().save(commit=False)
        if user:
            event.created_by = user
        if commit:
            event.save()
        return event


class EventCodeForm(forms.Form):
    """Form for entering event code to join"""

    code = forms.CharField(
        max_length=8,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter event code",
                "style": "text-transform: uppercase;",
            }
        ),
    )

    def clean_code(self):
        code = self.cleaned_data["code"].upper()
        try:
            Event.objects.get(code=code, is_active=True)
            return code
        except Event.DoesNotExist:
            raise forms.ValidationError("Invalid or inactive event code.")


class PhotoForm(forms.ModelForm):
    """Form for photo metadata"""

    class Meta:
        model = Photo
        fields = ["guest_name", "guest_email"]
        widgets = {
            "guest_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your name (optional)"}
            ),
            "guest_email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Your email (optional)"}
            ),
        }
