from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^add/$', views.add, name='add'),
    url(r'^remove/$', views.remove, name='remove'),
    url(r'^disable/$', views.disable, name='disable'),
    url(r'^enable/$', views.enable, name='enable'),
    url(r'^edit/(?P<username>\w+)/$', views.edit, name='edit'),
]
