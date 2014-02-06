from django import forms
from django.contrib.auth.models import Group
from django.db import models
from django.forms.models import (
    BaseModelFormSet, ModelForm, modelformset_factory, ValidationError)

from editorsnotes.main.models import User, Project, ProjectInvitation

class ProjectRoleField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.role.title()

def make_project_invitation_formset(project):
    """
    Create a project invitation formset for a project

    Cannot be done by a simple modelformset_factory because we need to create
    the Form and FormSet on the fly to take into account existing project
    invitations.
    """

    if not isinstance(project, Project):
        raise ValueError('{} is not a project.'.format(project))

    project_invitations = ProjectInvitation.objects.filter(project_id=project.id)

    class ProjectInvitationFormSet(BaseModelFormSet):
        def __init__(self, *args, **kwargs):
            kwargs['queryset'] = project_invitations
            super(ProjectInvitationFormSet, self).__init__(*args, **kwargs)

    class ProjectInvitationForm(ModelForm):
        project_role = ProjectRoleField(queryset=project.roles.all())
        class Meta:
            model = ProjectInvitation
            fields = ('email', 'project_role',)
        def __init__(self, *args, **kwargs):
            super(ProjectInvitationForm, self).__init__(*args, **kwargs)
            self.fields['email'].widget.attrs['placeholder'] = 'Email to invite'
        def clean_email(self):
            "Make sure email is unique for this project"
            data = self.cleaned_data['email']
            user = User.objects.filter(email=data)

            # Check if there are multiple users with this email address. If
            # there are, fail. In practice, there's no way this should actually
            # happen.
            if user.count() > 1:
                msg = 'Multiple users with this email address.'
                raise forms.ValidationError(msg)

            # Next, check if there is a user with this email already in the
            # project, and raise an error if there is.
            elif user.count() == 1 and project in user.get().get_affiliated_projects():
                msg = 'User with email {} already in project.'.format(data)
                raise forms.ValidationError(msg)

            # Next, check if there's already an invitation for this email
            # address.
            # TODO: Really, this should be a unique constraint on the model.
            existing_invite = ProjectInvitation.objects.filter(
                email=data, project_id=project.id)
            if not self.instance.id and existing_invite.count():
                msg = 'User with email {} already invited.'.format(data)
                raise forms.ValidationError(msg)

            return data

    return modelformset_factory(
        ProjectInvitation,
        formset=ProjectInvitationFormSet,
        form=ProjectInvitationForm,
        can_delete=True,
        extra=1
    )

def make_project_roster_formset(project):
    """
    Returns a formset for editing project roles.
    """
    if not isinstance(project, Project):
        raise ValueError('{} is not a project.'.format(project))

    project_roster = project.members.order_by('-last_login')

    class ProjectRosterFormSet(BaseModelFormSet):
        def __init__(self, *args, **kwargs):
            kwargs['queryset'] = project_roster
            super(ProjectRosterFormSet, self).__init__(*args, **kwargs)

    class ProjectMemberForm(ModelForm):
        project_role = ProjectRoleField(queryset=project.roles.all())
        class Meta:
            model = User
        def __init__(self, *args, **kwargs):
            super(ProjectMemberForm, self).__init__(*args, **kwargs)
            if not self.instance.pk:
                return
            self.initial['project_role'] = project.get_role_for(self.instance)
        def save(self, commit=True):
            user = self.instance
            existing_role = project.get_role_for(user)
            if existing_role != self.cleaned_data['project_role']:
                old_role = user.groups.get(name__startswith='{}_'.format(
                    project.slug))
                new_role = Group.objects.get(name__startswith='{}_{}'.format(
                    project.slug, self.cleaned_data['project_role']))
                user.groups.remove(old_role)
                user.groups.add(new_role)
            user.save()
            return user

    return modelformset_factory(
        User,
        formset=ProjectRosterFormSet,
        form=ProjectMemberForm,
        fields=(),
        extra=0
    )

BANNED_PROJECT_SLUGS = (
    'add',
)

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ('slug',)

class ProjectCreationForm(ModelForm):
    """
    Form for creating a project. Must be passed a user.
    """
    join_project = forms.BooleanField(initial=True,
                                      help_text='Join project after creation?')
    class Meta:
        model = Project
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ProjectCreationForm, self).__init__(*args, **kwargs)
        self.user = user
    def clean_slug(self):
        data = self.cleaned_data['slug']
        if data in BANNED_PROJECT_SLUGS:
            raise ValidationError('This slug is a reserved word.')
        return data
    def save(self, *args, **kwargs):
        obj = super(ProjectCreationForm, self).save()
        if self.cleaned_data['join_project']:
            role = obj.roles.get(role='Editor')
            role.users.add(self.user)
        return obj


