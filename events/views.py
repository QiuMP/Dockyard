from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import Event


@login_required
@permission_required('events.view_events', raise_exception=True)
def index(request):
    data = {
        'event_list': Event.objects.order_by('-time')
    }

    return render(request, 'events/index.djhtml', data)


@login_required
@require_http_methods(["POST"])
@permission_required('events.modify_events', raise_exception=True)
def clean(request):
    Event.objects.all().delete()
    return redirect(reverse('events:index'))
