from django.shortcuts import redirect, render

from rbsocialauth.forms import UsernameForm


def prompt_username(request):
    partial_pipeline = request.session['partial_pipeline']

    if request.method == 'POST':
        form = UsernameForm(request.POST)

        if form.is_valid():
            request.session['saved_username'] = form.cleaned_data['username']
            backend = partial_pipeline['backend']

            return redirect('social:complete', backend=backend)
    else:
        form = UsernameForm(initial={
            'username': partial_pipeline['kwargs']['username'],
        })

    return render(request, 'rbsocialauth/username_form.html', {
        'form': form,
    })
