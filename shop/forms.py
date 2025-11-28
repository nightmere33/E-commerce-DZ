from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'votre@email.com'
        }),
        label="Adresse email"
    )
    referral_code_input = forms.CharField(  # Changed field name to avoid conflict
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Code de parrainage (optionnel)'
        }),
        help_text='Si un ami vous a parrainé, entrez son code ici',
        label="Code de parrainage"
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'referral_code_input')  # ADD referral_code_input HERE
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['email', 'referral_code_input']:  # Already styled
                field.widget.attrs.update({
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                    'placeholder': field.label
                })
            
            # Update labels to be more user-friendly
            if field_name == 'username':
                field.label = "Nom d'utilisateur"
                field.widget.attrs['placeholder'] = "Choisissez un nom d'utilisateur"
            elif field_name == 'password1':
                field.label = "Mot de passe"
                field.widget.attrs['placeholder'] = "Créez un mot de passe sécurisé"
            elif field_name == 'password2':
                field.label = "Confirmation du mot de passe"
                field.widget.attrs['placeholder'] = "Confirmez votre mot de passe"
        
        # Update help texts
        self.fields['password1'].help_text = """
            <ul class="text-xs text-gray-600 mt-1 space-y-1">
                <li>• Au moins 8 caractères</li>
                <li>• Pas trop commun</li>
                <li>• Pas entièrement numérique</li>
            </ul>
        """
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Un utilisateur avec cet email existe déjà.")
        return email

    def clean_referral_code_input(self):
        code = self.cleaned_data.get('referral_code_input')
        if code:
            # Remove any spaces and convert to uppercase
            code = code.strip().upper()
            try:
                referrer = CustomUser.objects.get(referral_code=code)
                if referrer == self.instance:  # Can't refer yourself
                    raise ValidationError("Vous ne pouvez pas utiliser votre propre code de parrainage.")
            except CustomUser.DoesNotExist:
                raise ValidationError("Code de parrainage invalide.")
        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # Handle referral code
        referral_code = self.cleaned_data.get('referral_code_input')
        if referral_code:
            try:
                referrer = CustomUser.objects.get(referral_code=referral_code)
                user.referred_by = referrer
            except CustomUser.DoesNotExist:
                pass  # This shouldn't happen due to validation, but just in case
        
        if commit:
            user.save()
        
        # After saving the user, if there is a referrer, add points to both users
        if user.referred_by:
            referrer = user.referred_by
            # Add 1 point to the referrer
            referrer.points += 1
            referrer.save(update_fields=['points'])
            
            # Add 1 point to the new user as welcome bonus
            user.points += 1
            user.save(update_fields=['points'])
        
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': "Nom d'utilisateur"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Mot de passe'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['password'].label = "Mot de passe"