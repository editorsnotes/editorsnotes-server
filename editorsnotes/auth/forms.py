from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from rest_framework.authtoken.models import Token

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
    create_token = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('display_name', 'email', 'create_token',)

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True

        try:
            token = Token.objects.get(user=self.instance)
        except Token.DoesNotExist:
            token = None

        self.EXISTING_TOKEN = token

    def clean_email(self):
        return self.instance.email

    def save(self):
        super(UserProfileForm, self).save()
        if self.cleaned_data['create_token']:
            Token.objects.filter(user=self.instance).delete()
            token, created = Token.objects.get_or_create(user=self.instance)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'slug', 'default_license',)
