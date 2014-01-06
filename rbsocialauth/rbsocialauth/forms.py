from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from djblets.extensions.forms import SettingsForm


class SocialAuthSettingsForm(SettingsForm):
    enable_external_register = forms.BooleanField(
        label=_('Enable registration through external services'),
        help_text=_('Allows users to register with enabled external '
                    'authentication providers, like OpenID or GitHub.'),
        required=False)

    enable_openid = forms.BooleanField(
        label=_('Enable OpenID authentication'),
        help_text=_('Allows users to log in with OpenID.'),
        required=False)

    enable_github = forms.BooleanField(
        label=_('Enable GitHub authentication'),
        help_text=_('Allow users to log in with GitHub.'),
        required=False)

    enable_google = forms.BooleanField(
        label=_('Enable Google authentication'),
        help_text=_('Allow users to log in with Google.'),
        required=False)

    github_client_id = forms.CharField(
        label=_('GitHub Client ID'),
        required=False,
        widget=forms.TextInput(attrs={'size': 50}))

    github_client_secret = forms.CharField(
        label=_('GitHub Client Secret'),
        required=False,
        widget=forms.TextInput(attrs={'size': 50}))

    def clean(self):
        cleaned_data = super(SocialAuthSettingsForm, self).clean()

        if (cleaned_data['enable_github'] and
            (not cleaned_data['github_client_id'] or
             not cleaned_data['github_client_secret'])):

            error = forms.util.ErrorList([
                _('This field is required when enabling GitHub '
                  'authentication.'),
            ])
            self.errors['github_client_id'] = error
            self.errors['github_client_secret'] = error

        return cleaned_data


class UsernameForm(forms.Form):
    username = forms.CharField(
        label=_('Username'),
        help_text=_('Enter the username you want to identify yourself as.'),
        required=True,
        widget=forms.TextInput(attrs={'size': 30}))

    def clean_username(self):
        username = self.cleaned_data['username'].strip()

        try:
            User.objects.get(username=username)
            raise forms.ValidationError([_('This username is already taken')])
        except User.DoesNotExist:
            return username
