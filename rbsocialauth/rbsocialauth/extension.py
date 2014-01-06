from django import forms
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from djblets.extensions.signals import settings_saved
from reviewboard.accounts.forms.pages import AccountPageForm
from reviewboard.extensions.base import Extension
from reviewboard.extensions.hooks import (AccountPageFormsHook, TemplateHook,
                                          URLHook)
from reviewboard.signals import site_settings_loaded
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from social.apps.django_app.utils import Storage, BACKENDS
from social.backends.utils import load_backends, user_backends_data


class AccountIdentitiesForm(AccountPageForm):
    form_id = 'socialauth-identities'
    form_title = _('OpenID Identities')
    save_label = None
#    template_name = 'rbsocialauth/account_form.html'

    js_view_class = 'RBSocialAuth.ConnectedIdentitiesView'

    def get_js_view_data(self):
        user = self.request.user
        storage = Storage
        backends = user_backends_data(user, BACKENDS, storage)

        data = {
            'identities': [
                {
                    'uid': identity.uid,
                    'provider': identity.provider,
                    'allowedToDisconnect': storage.allowed_to_disconnect(
                        user, identity.provider, identity.id),
                    'disconnectURL': reverse(
                        'social:disconnect_individual',
                        args=[identity.provider, identity.id]),
                }
                for identity in backends.get('associated', [])
            ],
        }
        data.update(csrf(self.request))

        return data


class SocialAuthExtension(Extension):
    metadata = {
        'Name': _('Social Authentication'),
        'Summary': _('Allows users to log in through common OpenID/OAuth '
                     'services, such as GitHub, Google, Facebook, and '
                     'others.'),
    }

    apps = [
        'social.apps.django_app.default',
    ]

    context_processors = [
        'social.apps.django_app.context_processors.backends',
        'social.apps.django_app.context_processors.login_redirect',
    ]

    middleware = [
        SocialAuthExceptionMiddleware,
    ]

    default_settings = {
        'enable_external_register': False,
        'enable_openid': False,
        'enable_github': False,
        'enable_google': False,
        'github_client_id': None,
        'github_client_secret': None,
    }

    js_bundles = {
        'prefs': {
            'source_filenames': (
                'js/rbsocialauth.js',
            ),
            'apply_to': ['user-preferences'],
        },
    }

    css_bundles = {
        'login': {
            'source_filenames': (
                'css/font-awesome.min.css',
                'css/social-buttons.css',
                'css/login.css',
            ),
            'apply_to': ['login'],
        },
        'prefs': {
            'source_filenames': (
                'css/account_prefs.less',
            ),
            'apply_to': ['user-preferences'],
        },
    }

    is_configurable = True

    def initialize(self):
        settings_saved.connect(self.apply_social_auth_settings, sender=self)
        site_settings_loaded.connect(self.apply_social_auth_settings)

        self.apply_common_social_auth_settings()
        self.apply_social_auth_settings()

        AccountPageFormsHook(self, 'authentication', [AccountIdentitiesForm])

        URLHook(self, patterns(
            '',

            url('', include('social.apps.django_app.urls',
                            namespace='social')),
            url('^account/social/username/$',
                'rbsocialauth.views.prompt_username',
                name='rbsocialauth_prompt_username'),
        ))

        TemplateHook(self, 'after-login-form',
                     template_name='rbsocialauth/login.html')

    def apply_common_social_auth_settings(self):
        prefs_url = reverse('user-preferences')

        settings.SOCIAL_AUTH_LOGIN_REDIRECT_URL = reverse('dashboard')
        settings.SOCIAL_AUTH_NEW_USER_REDIRECT_URL = prefs_url
        settings.SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = prefs_url
        settings.SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = prefs_url
        settings.SOCIAL_AUTH_DISCONNECT_PIPELINE = (
            'social.pipeline.disconnect.allowed_to_disconnect',
            'social.pipeline.disconnect.get_entries',
            'social.pipeline.disconnect.revoke_tokens',
            'social.pipeline.disconnect.disconnect',
        )

        # XXX It's terrible that we have to set this, but django-social-auth
        #     breaks otherwise with a "... is not JSON serializable" error.
        settings.SESSION_SERIALIZER = \
            'django.contrib.sessions.serializers.PickleSerializer'

    def apply_social_auth_settings(self, *args, **kwargs):
        enable_openid = self.settings.get('enable_openid')

        # OpenID support
        self._apply_settings(
            'enable_openid',
            'AUTHENTICATION_BACKENDS', [
                'social.backends.open_id.OpenIdAuth',
            ])

        # GitHub support
        self._apply_settings(
            'enable_github',
            'AUTHENTICATION_BACKENDS', [
                'social.backends.github.GithubOAuth2',
            ])
        settings.SOCIAL_AUTH_GITHUB_KEY = self.settings.get('github_client_id')
        settings.SOCIAL_AUTH_GITHUB_SECRET = \
            self.settings.get('github_client_secret')

        # Google support
        self._apply_settings(
            'enable_google',
            'AUTHENTICATION_BACKENDS', [
                'social.backends.google.GoogleOpenId',
            ])

        # General authentication pipeline settings
        settings.SOCIAL_AUTH_PIPELINE = [
            'social.pipeline.social_auth.social_details',
            'social.pipeline.social_auth.social_uid',
            'social.pipeline.social_auth.auth_allowed',
            'social.pipeline.social_auth.social_user',
            'social.pipeline.user.get_username',
            'social.pipeline.mail.mail_validation',
        ]

        if self.settings.get('enable_external_register'):
            settings.SOCIAL_AUTH_PIPELINE += [
                'rbsocialauth.social_pipelines.prompt_username',
                'social.pipeline.user.create_user',
            ]

        settings.SOCIAL_AUTH_PIPELINE += [
            'social.pipeline.social_auth.associate_user',
            'social.pipeline.social_auth.load_extra_data',
            'social.pipeline.user.user_details',
        ]

        load_backends(settings.AUTHENTICATION_BACKENDS, force_load=True)

    def _apply_settings(self, enable_key, setting_name, values):
        setting = getattr(settings, setting_name, [])

        if isinstance(setting, tuple):
            setting = list(setting)

        if self.settings.get(enable_key):
            for value in values:
                if value not in setting:
                    setting.append(value)
        else:
            for value in values:
                try:
                    setting.remove(value)
                except ValueError:
                    pass

        setattr(settings, setting_name, setting)
