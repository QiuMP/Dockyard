from django.contrib import messages
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from events.models import Event


def _create_event(user, operation):
    Event.objects.create(user=user, type='A', operation=operation)


@login_required
def index(request):
    if not request.user.is_superuser:
        messages.info(request, 'Your are not Adminstrator, can only modify your own account.')
        return redirect(reverse('accounts:edit', args=(request.user.username,)))

    user_list = []
    for user in User.objects.all():
        permission_list = []

        if user.is_superuser:
            permission_list.append('Adminstrator')
        else:
            if not user.is_active:
                user.is_active = True
                user.save()

                all_permissions = user.get_all_permissions()

                user.is_active = False
                user.save()
            else:
                all_permissions = user.get_all_permissions()

            for permission in all_permissions:
                permission = permission.split('.')
                if permission[1].startswith('view'):
                    if permission[0] not in permission_list:
                        permission_list.append(permission[0] + ' Read Only')
                if permission[1].startswith('modify'):
                    permission_list.append(permission[0])
                    if permission[0] + ' Read Only' in permission_list:
                        permission_list.remove(permission[0] + ' Read Only')

        user_list.append({
            'is_active': user.is_active,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'permission_list': permission_list,
        })

    data = {
        'user_list': user_list,
    }
    return render(request, 'accounts/index.djhtml', data)


@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login_user(request, user)
                return redirect(reverse('index'))
            else:
                messages.error(request, 'Your account is disabled.')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.djhtml')


@login_required
def logout(request):
    logout_user(request)
    return redirect(reverse('accounts:login'))


@login_required
@require_http_methods(["GET", "POST"])
@permission_required('auth.add_user', raise_exception=True)
def add(request):
    if request.method == 'POST':
        post = request.POST
        username = post.get('username')

        if User.objects.filter(username=username):
            messages.error(request, 'User "' + username + '" exists.')
            return render(request, 'accounts/add.djhtml')

        user_args = {
            'username': username,
            'first_name': post.get('firstname'),
            'last_name': post.get('lastname'),
            'password': post.get('password'),
        }

        try:
            user = User.objects.create_user(**user_args)

            if post.get('adminstrator') == 'yes':
                user.is_superuser = True
            else:
                for key in ('nodes', 'containers', 'images',
                            'events'):
                    if not post.get(key):
                        continue

                    view_permission = Permission.objects.get(codename='view_'+key)
                    modify_permission = Permission.objects.get(codename='modify_'+key)
                    if post.get(key) == "read":
                        user.user_permissions.add(view_permission)
                    elif post.get(key) == "all":
                        user.user_permissions.add(view_permission)
                        user.user_permissions.add(modify_permission)

            user.save()
            _create_event(request.user, 'Add user "' + username + '".')
            messages.info(request, 'Add user "' + username + '" success.')
        except Exception, message:
            messages.error(request, message)

        return redirect(reverse('accounts:index'))
    return render(request, 'accounts/add.djhtml')


@login_required
@require_http_methods(["GET", "POST"])
def edit(request, username):
    if request.user.username != username and not request.user.is_superuser:
        messages.error(request, 'You are not Adminstrator, can only modify your own account.')
        return redirect(reverse('accounts:edit', args=(request.user.username,)))

    if not User.objects.filter(username=username):
        messages.error(request, 'User "' + username + '" does not exist.')
        return redirect(reverse('accounts:index'))

    if request.method == "POST":
        post = request.POST

        try:
            user = User.objects.get(username=username)

            user.first_name = post.get('firstname')
            user.last_name = post.get('lastname')

            if post.get('password'):
                user.set_password(post.get('password'))

            if request.user.is_superuser and request.user.username != username:
                if post.get('adminstrator') == 'yes':
                    user.is_superuser = True
                else:
                    user.is_superuser = False
                    for key in ('nodes', 'containers', 'images',
                                'events'):
                        if not post.get(key):
                            continue

                        view_permission = Permission.objects.get(codename='view_'+key)
                        modify_permission = Permission.objects.get(codename='modify_'+key)
                        if post.get(key) == "read":
                            user.user_permissions.remove(modify_permission)
                            user.user_permissions.add(view_permission)
                        elif post.get(key) == "all":
                            user.user_permissions.add(view_permission)
                            user.user_permissions.add(modify_permission)
                        else:
                            user.user_permissions.remove(view_permission)
                            user.user_permissions.remove(modify_permission)

            user.save()
            _create_event(request.user, 'Modify user "' + username + '".')
            messages.info(request, 'Modify user "' + username + '" success.')
        except Exception, message:
            messages.error(request, message)

        return redirect(reverse('accounts:index'))
    else:
        user = User.objects.get(username=username)
        if not user.is_active:
            user.is_active = True
            user.save()

            permissions = user.get_all_permissions()

            user.is_active = False
            user.save()
        else:
            permissions = user.get_all_permissions()

        data = {
            'modify_user': user,
            'permissions': permissions,
        }
        return render(request, 'accounts/edit.djhtml', data)


@login_required
@require_http_methods(["POST"])
@permission_required('auth.change_user', raise_exception=True)
def remove(request):
    username = request.POST.get('username', '')

    if username == request.user.username:
        messages.error(request, 'Cannot remove yourself !')
        return redirect(reverse('accounts:index'))

    if username:
        try:
            User.objects.get(username=username).delete()
            _create_event(request.user, 'Remove user "' + username + '".')
            messages.info(request, 'Remove user "' + username + '" success.')
        except Exception, message:
            messages.error(request, message)

    return redirect(reverse('accounts:index'))


@login_required
@require_http_methods(["POST"])
@permission_required('auth.change_user', raise_exception=True)
def disable(request):
    username = request.POST.get('username', '')

    if username == request.user.username:
        messages.error(request, 'Cannot disable yourself !')
        return redirect(reverse('accounts:index'))

    if username:
        try:
            user = User.objects.get(username=username)
            user.is_active = False
            user.save()

            _create_event(request.user, 'Disable user "' + username + '".')
            messages.info(request, 'Disable user "' + username + '" success.')
        except Exception, message:
            messages.error(request, message)

    return redirect(reverse('accounts:index'))


@login_required
@require_http_methods(["POST"])
@permission_required('auth.change_user', raise_exception=True)
def enable(request):
    username = request.POST.get('username', '')

    if username == request.user.username:
        messages.error(request, 'Cannot enable yourself !')
        return redirect(reverse('accounts:index'))

    if username:
        try:
            user = User.objects.get(username=username)
            user.is_active = True
            user.save()

            _create_event(request.user, 'Enable user "' + username + '".')
            messages.info(request, 'Enable user "' + username + '" success.')
        except Exception, message:
            messages.error(request, message)

    return redirect(reverse('accounts:index'))
