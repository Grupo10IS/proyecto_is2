# -*- coding:utf-8 -*-
import datetime
import os

from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .configs import MDConfig

MDEDITOR_CONFIGS = MDConfig("default")


# FUTURE: custom uploader goes here


class UploadView(generic.View):
    """upload image file"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        upload_image = request.FILES.get("editormd-image-file", None)

        # image none check
        if not upload_image:
            return JsonResponse(
                {"success": 0, "message": "No image to upload", "url": ""}
            )

        # image format check
        file_name_list = upload_image.name.split(".")
        file_extension = file_name_list.pop(-1)
        file_name = ".".join(file_name_list)
        if file_extension not in MDEDITOR_CONFIGS["upload_image_formats"]:
            return JsonResponse(
                {
                    "success": 0,
                    "message": "Invalid image extension：%s"
                    % ",".join(MDEDITOR_CONFIGS["upload_image_formats"]),
                    "url": "",
                }
            )

        # TODO: hacer que cambie segun sea entorno de tests o de produccion
        upload_local(file_name, file_extension, upload_image)


def upload_local(file_name, file_extension, upload_image):
    # image folder check
    media_root = settings.MEDIA_ROOT
    file_path = os.path.join(media_root, MDEDITOR_CONFIGS["image_folder"])
    if not os.path.exists(file_path):
        try:
            os.makedirs(file_path)
        except Exception as err:
            return JsonResponse(
                {"success": 0, "message": "上传失败：%s" % str(err), "url": ""}
            )

    # save image
    file_full_name = "%s_%s.%s" % (
        file_name,
        "{0:%Y%m%d%H%M%S%f}".format(datetime.datetime.now()),
        file_extension,
    )
    with open(os.path.join(file_path, file_full_name), "wb+") as file:
        for chunk in upload_image.chunks():
            file.write(chunk)

    return JsonResponse(
        {
            "success": 1,
            "message": "上传成功！",
            "url": os.path.join(
                settings.MEDIA_URL, MDEDITOR_CONFIGS["image_folder"], file_full_name
            ),
        }
    )
