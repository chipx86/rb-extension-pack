from django.conf.urls import patterns, url

from rbsocialauth.extension import SocialAuthExtension
from rbsocialauth.forms import SocialAuthSettingsForm


urlpatterns = patterns(
    '',

    url(r'^$', 'reviewboard.extensions.views.configure_extension',
        {
            'ext_class': SocialAuthExtension,
            'form_class': SocialAuthSettingsForm,
        }),
)
