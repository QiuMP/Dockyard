import socket

import docker
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def _get_client(url="tcp://192.168.248.101:5000"):
    return docker.from_env(version='auto', environment={"DOCKER_HOST": url})


@login_required
def index(request):
    client = _get_client()

    node_list = []

    try:
        for node in client.nodes.list():
            attrs = node.attrs
            spec = attrs['Spec']
            desc = attrs['Description']
            resrc = desc['Resources']
            plat = desc['Platform']

            try:
                if 'ManagerStatus' in attrs:
                    address = attrs['ManagerStatus']['Addr']
                else:
                    address = socket.gethostbyname(desc['Hostname'])
            except:
                address = False

            try:
                # if socket.gethostbyname(desc['Hostname']).startswith('127.'):
                if socket.gethostbyname(desc['Hostname']).endswith('101'):
                    containers = [
                        len(client.containers.list(filters={'status': 'running'}))
                        + len(client.containers.list(filters={'status': 'restarting'})),
                        len(client.containers.list(filters={'status': 'paused'})),
                        len(client.containers.list(filters={'status': 'exited'}))
                        + len(client.containers.list(filters={'status': 'created'})),
                    ]
                else:
                    containers = False
            except:
                containers = False

            node_list.append({
                'status': attrs['Status']['State'],
                'availability': spec['Availability'],
                'role': spec['Role'],
                'short_id': node.short_id,
                'id': node.id,
                'hostname': desc['Hostname'],
                'address': address if address else '(unknown)',
                'containers': containers,
                'platform': plat['OS'] + '/' + plat['Architecture'],
                'cpus': resrc['NanoCPUs'] / 1000000000,
                'memory': resrc['MemoryBytes'] / 1000000,
            })
    except:
        node_list = []

    data = {
        'node_list': node_list,
    }
    return render(request, 'nodes/index.djhtml', data)
