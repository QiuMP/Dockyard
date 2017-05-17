from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^services/', include('services.urls', namespace='services')),
    url(r'^containers/', include('containers.urls', namespace='containers')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^events/', include('events.urls', namespace='events')),
    url(r'^images/', include('images.urls', namespace='images')),
    url(r'^nodes/', include('nodes.urls', namespace='nodes')),
]

handler403 = 'dockyard.views.permission_denied'
handler404 = 'dockyard.views.page_not_found'
