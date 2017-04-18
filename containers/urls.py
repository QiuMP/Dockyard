from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^deploy/$', views.deploy, name='deploy'),
    url(r'^start/$', views.start, name='start'),
    url(r'^restart/$', views.restart, name='restart'),
    url(r'^stop/$', views.stop, name='stop'),
    url(r'^pause/$', views.pause, name='pause'),
    url(r'^unpause/$', views.unpause, name='unpause'),
    url(r'^destroy/$', views.destroy, name='destroy'),
    url(r'^rename/$', views.rename, name='rename'),
    url(r'^commit/$', views.commit, name='commit'),
    url(r'^(?P<container_id>\w+)/$', views.detail, name='detail'),
    url(r'^(?P<container_id>\w+)/logs/$', views.logs, name='logs'),
]
