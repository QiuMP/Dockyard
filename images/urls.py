from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pull/$', views.pull, name='pull'),
    url(r'^remove/$', views.remove, name='remove'),
    url(r'^edit/$', views.edit, name='edit'),
]
