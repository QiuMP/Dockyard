from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


def index(request):
    user = request.user
    if user.has_perm('nodes.view_nodes'):
        return HttpResponseRedirect(reverse('nodes:index'))
    if user.has_perm('containers.view_containers'):
        return HttpResponseRedirect(reverse('containers:index'))
    if user.has_perm('images.view_images'):
        return HttpResponseRedirect(reverse('images:index'))
    return HttpResponseRedirect(reverse('accounts:index'))


@login_required
def permission_denied(request):
    return render(request, '403.djhtml')


@login_required
def page_not_found(request):
    return render(request, '404.djhtml')
