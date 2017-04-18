# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

# from ..images.models import Image


# @require_http_methods(['POST'])
# def images(request):
#     """
#     处理服务器发过来的镜像信息
#     """
#     # TODO: 验证服务器，与 Node 相关

#     image_data = json.loads(request.body)
#     for i in image_data:
#         image, created = Image.objects.get_or_create(image_id=i.get('Id'))

#     return HttpResponse()
