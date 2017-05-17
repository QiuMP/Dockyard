import re

import docker
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from events.models import Event

from .models import Node


def _get_client(url):
    return docker.from_env(version='auto', environment={"DOCKER_HOST": url})


def _create_event(user, operation):
    Event.objects.create(user=user, type='N', operation=operation)


@login_required
@permission_required('nodes.view_nodes', raise_exception=True)
def index(request):
    node_list = []

    for node in Node.objects.all():
        node_info = {
            'name': node.name,
            'address': node.ip + ':' + str(node.port),
        }

        try:
            client = _get_client(node.get_address())

            info = client.info()

            try:
                containers = [
                    len(client.containers.list(filters={'status': 'running'}))
                    + len(client.containers.list(filters={'status': 'restarting'})),
                    len(client.containers.list(filters={'status': 'paused'})),
                    len(client.containers.list(filters={'status': 'exited'}))
                    + len(client.containers.list(filters={'status': 'created'})),
                ]
            except:
                containers = False

            node_info.update({
                'status': 'True',
                'containers': containers,
                'platform': info['OSType'] + '/' + info['Architecture'],
                'cpus': info['NCPU'],
                'memory': str(info['MemTotal'] / 1000000) + 'MB',
            })

        except:
            pass

        node_list.append(node_info)

    data = {
        'node_list': node_list,
    }

    return render(request, 'nodes/index.djhtml', data)


@login_required
@require_http_methods(["POST"])
@permission_required('nodes.modify_nodes', raise_exception=True)
def add(request):
    node_name = request.POST.get('node_name')
    node_ip = request.POST.get('node_ip')
    node_port = request.POST.get('node_port')

    if node_name and node_ip and node_port:
        try:
            if Node.objects.filter(name=node_name):
                raise Exception('Node "' + node_name + '" exists.')

            pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
            if node_ip == 'localhost':
                node_ip = '0.0.0.0'
            if not re.match(pattern, node_ip):
                raise Exception('Ip format error!')

            Node.objects.create(name=node_name,
                                ip=node_ip,
                                port=node_port)

            messages.add_message(request, messages.INFO, 'Add node "' + \
                                 node_name + '" success.')
            _create_event(request.user, 'Add node "' + \
                          node_name + '".')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message)

    return redirect(reverse('nodes:index'))


@login_required
@require_http_methods(["POST"])
@permission_required('nodes.modify_nodes', raise_exception=True)
def edit(request):
    node_name = request.POST.get('node_name')
    change_name = request.POST.get('change_name')

    if node_name and change_name and node_name != change_name:
        try:
            node = Node.objects.get(name=node_name)
            node.name = change_name
            node.save()

            messages.add_message(request, messages.INFO, 'Change node "' + \
                                 node_name + '" name to "' + \
                                 change_name + '" success.')
            _create_event(request.user, 'Change node "' + \
                          node_name + '" name to "' + \
                          change_name + '".')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message)

    return redirect(reverse('nodes:index'))


@login_required
@require_http_methods(["POST"])
@permission_required('nodes.modify_nodes', raise_exception=True)
def remove(request):
    node_name = request.POST.get('node_name')

    if node_name:
        try:
            Node.objects.get(name=node_name).delete()

            messages.add_message(request, messages.INFO, 'Remove node "' + \
                                 node_name + '" success.')
            _create_event(request.user, 'Remove node "' + \
                          node_name + '".')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message)

    return redirect(reverse('nodes:index'))
