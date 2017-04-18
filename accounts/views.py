from django.contrib import messages
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods


@login_required
def index(request):
    return render(request, 'accounts/index.djhtml')


@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login_user(request, user)
                return redirect(reverse('index'))
            else:
                messages.error(request, 'Your account is disabled.  Make sure you have activated your account.')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.djhtml')


@login_required
def logout(request):
    logout_user(request)
    return redirect(reverse('accounts:login'))
