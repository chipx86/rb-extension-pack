from django.shortcuts import redirect
from social.pipeline.partial import partial


@partial
def prompt_username(strategy, details, user=None, is_new=False,
                    username=None, *args, **kwargs):
    print '*** user = %r, is_new = %s' % (user, is_new)
    if strategy.session_get('saved_username'):
        return {
            'username': strategy.session_pop('saved_username'),
        }
    else:
        return redirect('rbsocialauth_prompt_username')
