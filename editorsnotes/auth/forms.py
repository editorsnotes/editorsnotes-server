from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, Project


class ENUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'display_name')

    def clean_email(self):
        # Since User.email is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )


class ENAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            if user.confirmed:
                raise forms.ValidationError('This account is inactive.')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'display_name',)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'slug', 'default_license',)
