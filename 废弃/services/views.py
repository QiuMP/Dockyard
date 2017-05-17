from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render


@login_required
@permission_required('services.view_services', raise_exception=True)
def index(request):
    return render(request, 'services/index.djhtml')
