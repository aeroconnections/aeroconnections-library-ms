from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class SetupPinForm(forms.Form):
    pin = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(attrs={
            "class": "search-input",
            "placeholder": "Enter setup PIN",
            "autocomplete": "off"
        }),
        label="Setup PIN"
    )


class SetupForm(forms.Form):
    library_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "search-input"}),
        label="Library Name",
        initial="Library Management System"
    )
    admin_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "search-input"}),
        label="Admin Username",
        initial="admin"
    )
    admin_email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "search-input"}),
        label="Admin Email"
    )
    admin_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "search-input"}),
        label="Admin Password",
        min_length=8
    )
    admin_password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "search-input"}),
        label="Confirm Password"
    )
    setup_pin = forms.CharField(
        max_length=6,
        min_length=4,
        widget=forms.PasswordInput(attrs={"class": "search-input"}),
        label="Setup PIN (4-6 digits)",
        help_text="Use this PIN to access setup page later",
        required=True
    )
    domain = forms.URLField(
        widget=forms.URLInput(attrs={"class": "search-input"}),
        label="Your Domain",
        help_text="The URL where this application will be accessed"
    )
    loan_duration = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "search-input"}),
        label="Loan Duration (days)",
        initial=30,
        min_value=1,
        max_value=365
    )
    due_soon_threshold = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "search-input"}),
        label="Due Soon Threshold (days)",
        initial=25,
        min_value=1,
        max_value=365
    )
    max_books_per_borrower = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "search-input"}),
        label="Max Books per Borrower",
        initial=5,
        min_value=1,
        max_value=50
    )

    def clean_admin_username(self):
        username = self.cleaned_data.get("admin_username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("admin_password")
        password_confirm = cleaned_data.get("admin_password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError("Passwords do not match.")

        return cleaned_data


class ChangePinForm(forms.Form):
    current_pin = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(attrs={"class": "search-input"}),
        label="Current PIN"
    )
    new_pin = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(attrs={"class": "search-input"}),
        label="New PIN"
    )
    confirm_pin = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(attrs={"class": "search-input"}),
        label="Confirm New PIN"
    )

    def clean(self):
        cleaned_data = super().clean()
        new_pin = cleaned_data.get("new_pin")
        confirm_pin = cleaned_data.get("confirm_pin")

        if new_pin and confirm_pin:
            if new_pin != confirm_pin:
                raise ValidationError("PINs do not match.")

        return cleaned_data
