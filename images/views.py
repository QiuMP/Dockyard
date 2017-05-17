from datetime import datetime

import docker
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from events.models import Event
from nodes.models import Node


def _get_client(url):
    return docker.from_env(version='auto', environment={"DOCKER_HOST": url})


def _create_event(user, node, operation):
    Event.objects.create(user=user, type='I', node=node, operation=operation)


@login_required
@permission_required('images.view_images', raise_exception=True)
def index(request):
    image_list = []

    for node in Node.objects.all():
        try:
            client = _get_client(node.get_address())

            for image in client.images.list(all=True):
                attrs = image.attrs
                image_list.append({
                    'node': node.name,
                    'tags': image.tags,
                    'short_id': image.short_id,
                    'id': image.id,
                    'created': datetime.fromtimestamp(attrs["Created"]),
                    'virtual_size': round(attrs["VirtualSize"] / 1000000.0, 2),
                })
        except:
            pass

    data = {
        'node_list': Node.objects.all(),
        'image_list': image_list,
    }

    return render(request, 'images/index.djhtml', data)


@login_required
@require_http_methods(["POST"])
@permission_required('images.modify_images', raise_exception=True)
def pull(request):
    pull_name = request.POST.get('pull_name')
    node_name = request.POST.get('node_name')
    if pull_name:
        try:
            node = Node.objects.get(name=node_name)
            client = _get_client(node.get_address())

            if len(pull_name.split(':')) == 1:
                pull_name += ':latest'

            client.images.pull(pull_name)
            messages.add_message(request, messages.INFO, 'Pull "' + \
                                 pull_name + '" success.')
            _create_event(request.user, node, 'Pull image "' + pull_name + '".')
        except Exception, message:
            messages.add_message(request, messages.ERROR, message)

    return redirect(reverse('images:index'))


@login_required
@require_http_methods(["POST"])
@permission_required('images.modify_images', raise_exception=True)
def remove(request):
    image_id = request.POST.get('image_id')
    node_name = request.POST.get('node_name')
    if image_id and node_name:
        try:
            node = Node.objects.get(name=node_name)
            client = _get_client(node.get_address())

            try:
                image_name = client.images.get(image_id).tags[0]
            except:
                image_name = image_id[:17]

            client.images.remove(image_id)
            messages.add_message(request, messages.INFO, 'Remove image "' + \
                                 image_name + '" success.')
            _create_event(request.user, node, 'Remove image "' + image_name + \
                          '".')
        except Exception, message:
            messages.add_message(request, messages.ERROR, message)

    return redirect(reverse('images:index'))


@login_required
@require_http_methods(["POST"])
@permission_required('images.modify_images', raise_exception=True)
def edit(request):
    tag_name = request.POST.get('tag_name').strip()
    image_id = request.POST.get('image_id')
    node_name = request.POST.get('node_name')

    if node_name and tag_name and image_id:
        try:
            node = Node.objects.get(name=node_name)
            client = _get_client(node.get_address())

            image = client.images.get(image_id)
            tag_list = []
            for tag in tag_name.split():
                if tag:
                    temp = tag.split(':')
                    if len(temp) == 1:
                        temp.append('latest')
                    image.tag(temp[0], temp[1])
                    tag_list.append(temp[0] + ':' + temp[1])

            if tag_list:
                for tag in image.tags:
                    if tag not in tag_list:
                        client.images.remove(tag)

                messages.add_message(request, messages.INFO, 'Edit image "' + \
                                     image_id + '" name to "' + \
                                     ' '.join(tag_list) + '" success.')
                _create_event(request.user, node,
                              'Edit image "' + image_id + '" name to "' + \
                              ' '.join(tag_list) + '".')
            else:
                messages.add_message(request, messages.ERROR, 'Format Error!')
        except Exception, message:
            messages.add_message(request, messages.ERROR, message)

    return redirect(reverse('images:index'))
