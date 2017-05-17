# -*- coding: utf-8 -*-

from datetime import datetime

import docker
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from events.models import Event
from nodes.models import Node


def _create_event(user, node, operation):
    Event.objects.create(user=user, type='C', node=node, operation=operation)


def _get_client(url="tcp://192.168.248.101:5000"):
    return docker.from_env(version='auto', environment={"DOCKER_HOST": url})


@login_required
@permission_required('containers.view_containers', raise_exception=True)
def index(request):
    container_list = []

    for node in Node.objects.all():
        try:
            client = _get_client(node.get_address())

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
                    'node': node.name,
                    'heart': container.status,
                    'name': container.name,
                    'short_id': container.short_id,
                    'id': container.id,
                    'image': image,
                    'status': status,
                    'created': created.__str__() + ' UTC',
                })
        except:
            pass

    data = {
        'container_list': container_list,
    }
    return render(request, 'containers/index.djhtml', data)


@login_required
@permission_required('containers.view_containers', raise_exception=True)
def detail(request, container_id):
    for _node in Node.objects.all():
        try:
            client = _get_client(_node.get_address())
            container = client.containers.get(container_id)
            node = _node
            break
        except:
            container = None

    if not container:  # 当容器没有找到的时候进行跳转
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
        'node': node.name,
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
                'network': net.capitalize(),
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
@permission_required('containers.view_containers', raise_exception=True)
def logs(request, container_id):
    for _node in Node.objects.all():
        try:
            client = _get_client(_node.get_address())
            container = client.containers.get(container_id)
            node = _node
            break
        except:
            container = None

    if not container:  # 当容器没有找到的时候进行跳转
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
@permission_required('containers.modify_containers', raise_exception=True)
def console(request, container_id):
    for _node in Node.objects.all():
        try:
            client = _get_client(_node.get_address())
            container = client.containers.get(container_id)
            node = _node
            break
        except:
            container = None

    if not container:  # 当容器没有找到的时候进行跳转
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
    }

    return render(request, 'containers/console.djhtml', data)


@login_required
@require_http_methods(["POST", "GET"])
@permission_required('containers.modify_containers', raise_exception=True)
def deploy(request):

    if request.method == "POST":
        container_vars = request.POST
        node_name = container_vars.get('node')
        create_vars = {
            'name': container_vars.get('name'),
            'image': container_vars.get('image'),
            'hostname': container_vars.get('hostname'),
            'domainname': container_vars.get('domainname'),
            'command': container_vars.get('command'),
            'cpu_period': container_vars.get('cpus'),
            'mem_limit': container_vars.get('memory'),
        }

        restart_policy = container_vars.get('restart_policy')
        if restart_policy and restart_policy != 'no':
            create_vars['restart_policy'] = {
                "Name": restart_policy,
            }

        variables_name = container_vars.getlist('variable_name')
        variables_value = container_vars.getlist('variable_value')
        environment = {}
        for name, value in zip(variables_name, variables_value):
            if name:
                environment[name] = value
        if environment:
            create_vars['environment'] = environment

        host_path = container_vars.getlist('host_path')
        container_path = container_vars.getlist('container_path')
        volumes = {}
        for host, container in zip(host_path, container_path):
            if host and container:
                volumes[host] = {
                    'bind': container,
                    'mode': 'rw',
                }
        if volumes:
            create_vars['volumes'] = volumes

        link_container = container_vars.getlist('link_container')
        link_alias = container_vars.getlist('link_alias')
        links = {}
        for container, alias in zip(link_container, link_alias):
            if container and alias:
                links[container] = alias
        if links:
            create_vars['links'] = links

        network_mode = container_vars.get('network_mode')
        if network_mode in ('bridge', 'host', 'none'):
            create_vars['network_mode'] = network_mode

        dns = container_vars.getlist('container_dns')
        if filter(None, dns):
            create_vars['dns'] = dns

        if request.POST.get('expose_all'):
            create_vars['publish_all_ports'] = True

        port_container = container_vars.getlist('port_container')
        port_protocol = container_vars.getlist('port_protocol')
        port_address = container_vars.getlist('port_address')
        port_host = container_vars.getlist('port_host')
        ports = {}

        for container, protocol, address, host in \
                zip(port_container, port_protocol, port_address, port_host):
            if container and protocol and host:
                ports[container + '/' + protocol] = (address, host) if address else host

        if ports:
            create_vars['ports'] = ports

        try:
            try:
                node = Node.objects.get(name=node_name)
                client = _get_client(node.get_address())
            except:
                messages.error(request, "Connection failed!")
                return redirect(reverse('containers:index'))

            container = client.containers.create(detach=True, **create_vars)
            messages.add_message(request, messages.INFO, 'Create container "' + \
                                 container.name + '" success.')
            _create_event(request.user, node, 'Create container "' + container.name + \
                          '".')
        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

        return redirect(reverse('containers:index'))

    else:
        client = _get_client(Node.objects.all()[0].get_address())
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
            'node_list': Node.objects.all(),
        }

        return render(request, 'containers/deploy.djhtml', data)


@login_required
@require_http_methods(["POST"])
@permission_required('containers.modify_containers', raise_exception=True)
def deploy_get(request):
    node_name = request.POST.get("node_name")

    if node_name:
        client = _get_client(Node.objects.get(name=node_name).get_address())
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

    return JsonResponse({
        'image_list': image_list,
        'container_list': container_list,
    })


@login_required
@require_http_methods(["POST"])
@permission_required('containers.modify_containers', raise_exception=True)
def start(request):
    container_name = request.POST.get('container_name')

    if container_name:
        try:
            for _node in Node.objects.all():
                try:
                    client = _get_client(_node.get_address())
                    container = client.containers.get(container_name)
                    node = _node
                    break
                except:
                    container = None

            if not container:  # 当容器没有找到的时候进行跳转
                messages.add_message(request, messages.ERROR,
                                     "Connection failed!")
                return redirect(request.META["HTTP_REFERER"])

            container.start()
            messages.add_message(request, messages.INFO, 'Start container "' + \
                                 container_name + '" success.')
            _create_event(request.user, node,
                          'Start container "' + container_name + '".')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
@permission_required('containers.modify_containers', raise_exception=True)
def restart(request):
    container_name = request.POST.get('container_name')

    if container_name:
        try:
            for _node in Node.objects.all():
                try:
                    client = _get_client(_node.get_address())
                    container = client.containers.get(container_name)
                    node = _node
                    break
                except:
                    container = None

            if not container:  # 当容器没有找到的时候进行跳转
                messages.add_message(request, messages.ERROR,
                                     "Connection failed!")
                return redirect(request.META["HTTP_REFERER"])

            container.restart()
            messages.add_message(request, messages.INFO, 'Restart container "' + \
                                 container_name + '" success.')
            _create_event(request.user, node,
                          'Restart container "' + container_name + '".')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
@permission_required('containers.modify_containers', raise_exception=True)
def stop(request):
    container_name = request.POST.get('container_name')

    if container_name:
        try:
            for _node in Node.objects.all():
                try:
                    client = _get_client(_node.get_address())
                    container = client.containers.get(container_name)
                    node = _node
                    break
                except:
                    container = None

            if not container:  # 当容器没有找到的时候进行跳转
                messages.add_message(request, messages.ERROR,
                                     "Connection failed!")
                return redirect(request.META["HTTP_REFERER"])

            container.stop()
            messages.add_message(request, messages.INFO, 'Stop container "' + \
                                 container_name + '" success.')
            _create_event(request.user, node,
                          'Stop container "' + container_name + '".')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
@permission_required('containers.modify_containers', raise_exception=True)
def pause(request):
    container_name = request.POST.get('container_name')

    if container_name:
        try:
            for _node in Node.objects.all():
                try:
                    client = _get_client(_node.get_address())
                    container = client.containers.get(container_name)
                    node = _node
                    break
                except:
                    container = None

            if not container:  # 当容器没有找到的时候进行跳转
                messages.add_message(request, messages.ERROR,
                                     "Connection failed!")
                return redirect(request.META["HTTP_REFERER"])

            container.pause()
            messages.add_message(request, messages.INFO, 'Pause container "' + \
                                 container_name + '" success.')
            _create_event(request.user, node,
                          'Pause container "' + container_name + '".')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
@permission_required('containers.modify_containers', raise_exception=True)
def unpause(request):
    container_name = request.POST.get('container_name')

    if container_name:
        try:
            for _node in Node.objects.all():
                try:
                    client = _get_client(_node.get_address())
                    container = client.containers.get(container_name)
                    node = _node
                    break
                except:
                    container = None

            if not container:  # 当容器没有找到的时候进行跳转
                messages.add_message(request, messages.ERROR,
                                     "Connection failed!")
                return redirect(request.META["HTTP_REFERER"])

            container.unpause()
            messages.add_message(request, messages.INFO, 'Unpause container "' + \
                                 container_name + '" success.')
            _create_event(request.user, node,
                          'Unpause container "' + container_name + '".')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
@permission_required('containers.modify_containers', raise_exception=True)
def destroy(request):
    container_name = request.POST.get('container_name')

    if container_name:
        try:
            for _node in Node.objects.all():
                try:
                    client = _get_client(_node.get_address())
                    container = client.containers.get(container_name)
                    node = _node
                    break
                except:
                    container = None

            if not container:  # 当容器没有找到的时候进行跳转
                messages.add_message(request, messages.ERROR,
                                     "Connection failed!")
                return redirect(request.META["HTTP_REFERER"])

            container.remove()
            messages.add_message(request, messages.INFO, 'Destroy container "' + \
                                 container_name + '" success.')
            _create_event(request.user, node,
                          'Destroy container "' + container_name + '".')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
@permission_required('containers.modify_containers', raise_exception=True)
def rename(request):
    container_name = request.POST.get('container_name')
    container_rename = request.POST.get('container_rename')

    if container_name and container_rename:
        try:
            for _node in Node.objects.all():
                try:
                    client = _get_client(_node.get_address())
                    container = client.containers.get(container_name)
                    node = _node
                    break
                except:
                    container = None

            if not container:  # 当容器没有找到的时候进行跳转
                messages.add_message(request, messages.ERROR,
                                     "Connection failed!")
                return redirect(request.META["HTTP_REFERER"])

            container.rename(container_rename)

            messages.add_message(request, messages.INFO, 'Rename container "' + \
                                 container_name + '" to "' + container_rename + \
                                 '" success.')
            _create_event(request.user, node,
                          'Rename container "' + container_name + \
                          '" to "' + container_rename + '".')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])


@login_required
@require_http_methods(["POST"])
@permission_required('containers.modify_containers', raise_exception=True)
def commit(request):
    container_name = request.POST.get('container_name')
    commit_name = request.POST.get('commit_name')

    if container_name and commit_name:
        try:
            for _node in Node.objects.all():
                try:
                    client = _get_client(_node.get_address())
                    container = client.containers.get(container_name)
                    node = _node
                    break
                except:
                    container = None

            if not container:  # 当容器没有找到的时候进行跳转
                messages.add_message(request, messages.ERROR,
                                     "Connection failed!")
                return redirect(request.META["HTTP_REFERER"])

            commit_name = commit_name.split(':')
            if len(commit_name) == 1:
                commit_name.append("latest")

            container.commit(commit_name[0], commit_name[1])

            messages.add_message(request, messages.INFO, 'Commit container "' + \
                                 container_name + '" to image "' + ':'.join(commit_name) + \
                                 '" success.')
            _create_event(request.user, node,
                          'Commit container "' + container_name + \
                          '" to image "' + ':'.join(commit_name) + '".')

        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(request.META["HTTP_REFERER"])
