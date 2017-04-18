# -*- coding: utf-8 -*-

from datetime import datetime

import docker
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from events.models import Event


def _create_event(user, operation):
    Event.objects.create(user=user, type='C', operation=operation)


def _get_client(url="tcp://192.168.248.101:5000"):
    try:
        return docker.from_env(version='auto', environment={"DOCKER_HOST": url})
    except:
        messages.add_message('Network error.')


@login_required
def index(request):
    client = _get_client()

    container_list = []

    try:
        for container in client.containers.list(True):
            attrs = container.attrs
            image = client.images.get(attrs['Image'])
            image = image.tags[0] if image.tags else image.short_id
            state = attrs['State']

            created = datetime.strptime(attrs['Created'].split('.')[0],
                                        '%Y-%m-%dT%H:%M:%S')
            if container.status in {'running', 'restarting', 'paused'}:
                status = 'Started at ' \
                         + datetime.strptime(state['StartedAt'].split('.')[0],
                                             '%Y-%m-%dT%H:%M:%S').__str__() + ' UTC'
            elif container.status == 'created':
                status = 'Created'
            else:
                status = 'Exited (' + str(state['ExitCode']) + ') at ' \
                         + datetime.strptime(state['FinishedAt'].split('.')[0],
                                             '%Y-%m-%dT%H:%M:%S').__str__() + ' UTC'

            container_list.append({
                'heart': container.status,
                'name': container.name,
                'short_id': container.short_id,
                'id': container.id,
                'image': image,
                'status': status,
                'created': created.__str__() + ' UTC',
            })
    except:
        container_list = []

    data = {
        'container_list': container_list,
    }
    return render(request, 'containers/index.djhtml', data)


@login_required
def detail(request, container_id):
    client = _get_client()

    try:
        container = client.containers.get(container_id)
    except:  # 当容器没有找到的时候进行跳转
        return redirect(reverse('containers:index'))

    attrs = container.attrs
    state = attrs['State']

    image = client.images.get(attrs['Image'])
    image = image.tags[0] if image.tags else image.short_id
    top = None

    created = datetime.strptime(attrs['Created'].split('.')[0],
                                '%Y-%m-%dT%H:%M:%S')
    if container.status in {'running', 'restarting', 'paused'}:
        status = 'Started at ' \
                    + datetime.strptime(state['StartedAt'].split('.')[0],
                                        '%Y-%m-%dT%H:%M:%S').__str__() + ' UTC'
        top = container.top()
    elif container.status == 'created':
        status = 'Never run'
    else:
        status = 'Exited (' + str(state['ExitCode']) + ') at ' \
                    + datetime.strptime(state['FinishedAt'].split('.')[0],
                                        '%Y-%m-%dT%H:%M:%S').__str__() + ' UTC'

    config = attrs['Config']
    entrypoint = ' '.join(config['Entrypoint']) if config['Entrypoint'] else None
    command = ' '.join(config['Cmd']) if config['Cmd'] else None

    container_config = {
        'name': container.name,
        'id': container.id,
        'short_id': container.short_id,
        'image': image,
        'status': status,
        'heart': container.status,
        'created': 'Created at ' + created.__str__() + ' UTC',
        'hostname': config['Hostname'],
        'domainname': config['Domainname'],
        'entrypoint': entrypoint,
        'command': command,
        'environment': config['Env'],
    }

    links = []
    hostconfig = attrs['HostConfig']
    try:
        for link in hostconfig['Links']:
            links.append(link.split(':'))
    except:
        links = []

    networksettings = attrs['NetworkSettings']
    networks = []
    try:
        for net, setting in networksettings['Networks'].items():
            networks.append({
                'network': net,
                'ipaddress': setting['IPAddress'],
                'ipprefixlen': setting['IPPrefixLen'],
                'gateway': setting['Gateway'],
                'ipv6address': setting['GlobalIPv6Address'],
                'ipv6prefixlen': setting['GlobalIPv6PrefixLen'],
                'ipv6gateway': setting['IPv6Gateway'],
                'mac': setting['MacAddress'],
            })
    except:
        networks = [

        ]

    ports = []
    try:
        for dst, srcs in networksettings['Ports'].items():
            if srcs:
                for src in srcs:
                    ports.append({
                        'src': src['HostIp'] + ':' + src['HostPort'],
                        'dst': dst,
                    })
            else:
                ports.append({
                    'src': None,
                    'dst': dst,
                })
    except:
        ports = []

    data = {
        'container': container_config,
        'networks': networks,
        'links': links,
        'ports': ports,
        'dns': hostconfig['Dns'],
        'processes': top,
    }

    return render(request, 'containers/detail.djhtml', data)


@login_required
def logs(request, container_id):
    client = _get_client()

    try:
        container = client.containers.get(container_id)
    except:  # 当容器没有找到的时候进行跳转
        return redirect(reverse('containers:index'))

    attrs = container.attrs
    state = attrs['State']

    image = client.images.get(attrs['Image'])
    image = image.tags[0] if image.tags else image.short_id

    created = datetime.strptime(attrs['Created'].split('.')[0],
                                '%Y-%m-%dT%H:%M:%S')
    if container.status in {'running', 'restarting', 'paused'}:
        status = 'Started at ' \
                    + datetime.strptime(state['StartedAt'].split('.')[0],
                                        '%Y-%m-%dT%H:%M:%S').__str__() + ' UTC'
        top = container.top()
    elif container.status == 'created':
        status = 'Never run'
    else:
        status = 'Exited (' + str(state['ExitCode']) + ') at ' \
                    + datetime.strptime(state['FinishedAt'].split('.')[0],
                                        '%Y-%m-%dT%H:%M:%S').__str__() + ' UTC'

    data = {
        'heart': container.status,
        'name': container.name,
        'image': image,
        'status': status,
        'created': 'Created at ' + created.__str__() + ' UTC',
        'logs': container.logs(stdout=True, stderr=True, timestamps=True)
    }

    return render(request, 'containers/logs.djhtml', data)


@login_required
@require_http_methods(["POST", "GET"])
def deploy(request):
    client = _get_client()

    if request.method == "POST":
        print request.POST.getlist('variable_name')
    else:
        image_list = []
        try:
            for image in client.images.list():
                image_list.append(image.tags[0])
        except:
            image_list = []

        container_list = []
        try:
            for container in client.containers.list(True):
                container_list.append(container.name)
        except:
            container_list = []

        data = {
            'image_list': image_list,
            'container_list': container_list,
        }

        return render(request, 'containers/deploy.djhtml', data)


@login_required
@require_http_methods(["POST"])
def start(request):
    client = _get_client()

    container_name = request.POST.get('container_name')

    if container_name:
        try:
            container = client.containers.get(container_name)
            container.start()
            messages.add_message(request, messages.INFO, 'Start container "' + \
                                 container_name + '" success.')
            _create_event(request.user, 'Start container "' + container_name + \
                          '"')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
def restart(request):
    client = _get_client()

    container_name = request.POST.get('container_name')

    if container_name:
        try:
            container = client.containers.get(container_name)
            container.restart()
            messages.add_message(request, messages.INFO, 'Restart container "' + \
                                 container_name + '" success.')
            _create_event(request.user, 'Restart container "' + container_name + \
                          '"')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
def stop(request):
    client = _get_client()

    container_name = request.POST.get('container_name')

    if container_name:
        try:
            container = client.containers.get(container_name)
            container.stop()
            messages.add_message(request, messages.INFO, 'Stop container "' + \
                                 container_name + '" success.')
            _create_event(request.user, 'Stop container "' + container_name + \
                          '"')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
def pause(request):
    client = _get_client()

    container_name = request.POST.get('container_name')

    if container_name:
        try:
            container = client.containers.get(container_name)
            container.pause()
            messages.add_message(request, messages.INFO, 'Pause container "' + \
                                 container_name + '" success.')
            _create_event(request.user, 'Pause container "' + container_name + \
                          '"')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
def unpause(request):
    client = _get_client()

    container_name = request.POST.get('container_name')

    if container_name:
        try:
            container = client.containers.get(container_name)
            container.unpause()
            messages.add_message(request, messages.INFO, 'Unpause container "' + \
                                 container_name + '" success.')
            _create_event(request.user, 'Unpause container "' + container_name + \
                          '"')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
def destroy(request):
    client = _get_client()

    container_name = request.POST.get('container_name')

    if container_name:
        try:
            container = client.containers.get(container_name)
            container.remove()
            messages.add_message(request, messages.INFO, 'Destroy container "' + \
                                 container_name + '" success.')
            _create_event(request.user, 'Destroy container "' + container_name + \
                          '"')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
def rename(request):
    client = _get_client()

    container_name = request.POST.get('container_name')
    container_rename = request.POST.get('container_rename')

    if container_name and container_rename:
        try:
            container = client.containers.get(container_name)
            container.rename(container_rename)

            messages.add_message(request, messages.INFO, 'Rename container "' + \
                                 container_name + '" to "' + container_rename + \
                                 '" success.')
            _create_event(request.user, 'Rename container "' + container_name + \
                          '" to "' + container_rename + '"')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
def commit(request):
    client = _get_client()

    container_name = request.POST.get('container_name')
    commit_name = request.POST.get('commit_name')

    if container_name and commit_name:
        try:
            container = client.containers.get(container_name)

            commit_name = commit_name.split(':')
            if len(commit_name) == 1:
                commit_name.append("latest")

            container.commit(commit_name[0], commit_name[1])

            messages.add_message(request, messages.INFO, 'Commit container "' + \
                                 container_name + '" to image "' + ':'.join(commit_name) + \
                                 '" success.')
            _create_event(request.user, 'Commit container "' + container_name + \
                          '" to image "' + ':'.join(commit_name) + '"')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])
