from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, Project

class ENUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(ENUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
    class Meta:
        model = User
        fields = ('username', 'email',)
    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

class ENAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            if user.confirmed:
                raise forms.ValidationError('This account is inactive.')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'slug', 'default_license',)
