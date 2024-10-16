from django import forms
from django.shortcuts import get_object_or_404, redirect
from .models import Reservation, UserAccount, Reservation, PCRental, PrintingOption 

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UserAccount
        fields = ['username', 'email', 'name', 'address', 'password1', 'password2', 'status']

    # Ensure the username is unique
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UserAccount.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    # Ensure the passwords match
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Hash the password
        user.status = 'customer'  # Automatically set status to 'customer'
        if commit:
            user.save()
        return user

class PCRentalForm(forms.ModelForm):
    class Meta:
        model = PCRental
        fields = ['pc_number', 'hourly_rate', 'is_available']

class PrintingOptionForm(forms.ModelForm):
    class Meta:
        model = PrintingOption
        fields = ['print_type', 'price_per_page', 'is_available']

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['pc_rental', 'printing_option', 'date', 'time', 'duration', 'number_of_pages', 'file', 'payment_status', 'discount', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pc_rental = cleaned_data.get('pc_rental')
        printing_option = cleaned_data.get('printing_option')
        duration = cleaned_data.get('duration')
        number_of_pages = cleaned_data.get('number_of_pages')
        file = cleaned_data.get('file')

        # Ensure one of the services is selected
        if not pc_rental and not printing_option:
            raise forms.ValidationError("You must select either a PC Rental or a Printing Option.")

        # Ensure valid fields based on the service type
        if pc_rental and not duration:
            raise forms.ValidationError("Duration is required for PC Rental.")
        elif printing_option:
            if not number_of_pages:
                raise forms.ValidationError("Number of pages is required for Printing.")
            if not file:
                raise forms.ValidationError("File is required for Printing.")

        return cleaned_data

