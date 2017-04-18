from datetime import datetime

import docker
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from events.models import Event


def _get_client(url="tcp://192.168.248.101:5000"):
    try:
        return docker.from_env(version='auto', environment={"DOCKER_HOST": url})
    except:
        messages.add_message('Network error.')


def _create_event(user, operation):
    Event.objects.create(user=user, type='I', operation=operation)


@login_required
def index(request):
    client = _get_client()

    image_list = []

    try:
        for image in client.images.list(all=True):
            attrs = image.attrs
            image_list.append({
                'tags': image.tags,
                'short_id': image.short_id,
                'id': image.id,
                'created': datetime.fromtimestamp(attrs["Created"]),
                'virtual_size': round(attrs["VirtualSize"] / 1000000.0, 2),
            })
    except:
        image_list = []

    data = {
        'image_list': image_list,
    }

    return render(request, 'images/index.djhtml', data)


@login_required
@require_http_methods(["POST"])
def pull(request):
    client = _get_client()

    pull_name = request.POST.get('pull_name')
    if pull_name:
        try:
            if len(pull_name.split(':')) == 1:
                pull_name += ':latest'

            client.images.pull(pull_name)
            messages.add_message(request, messages.INFO, 'Pull "' + \
                                 pull_name + '" success.')
            _create_event(request.user, 'Pull image "' + pull_name + '"')
        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(reverse('images:index'))


@login_required
@require_http_methods(["POST"])
def remove(request):
    client = _get_client()

    image_id = request.POST.get('image_id')
    if image_id:
        try:
            try:
                image_name = client.images.get(image_id).tags[0]
            except:
                image_name = image_id[:17]

            client.images.remove(image_id)
            messages.add_message(request, messages.INFO, 'Remove image "' + \
                                 image_name + '" success.')
            _create_event(request.user, 'Remove image "' + image_name + \
                          '"')
        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(reverse('images:index'))


@login_required
@require_http_methods(["POST"])
def edit(request):
    client = _get_client()

    tag_name = request.POST.get('tag_name').strip()
    image_id = request.POST.get('image_id')
    if tag_name:
        try:
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
                _create_event(request.user, 'Edit image "' + image_id + '" name to "' + \
                              ' '.join(tag_list) + '"')
            else:
                messages.add_message(request, messages.ERROR, 'Format Error!')
        except Exception, message:
            messages.add_message(request, messages.ERROR, message.explanation)

    return redirect(reverse('images:index'))
