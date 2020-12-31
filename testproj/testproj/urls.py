import os

from django.urls import include, path
from django.conf import settings

from drf_typescript_api_client import generate_api_client

urlpatterns = [
    path('api/v1/', include('api.urls')),
]


def post_processor(content):
    return """// @ts-nocheck
/* eslint-disable */

/** This file was generated automatically by drf-typescript-api-client.
* It should be in .gitignore, and you should not edit it;
* its contents will be overwritten automatically every time
* the Django server is run. See https://github.com/ryan.laney/drf-typescript-api-client
* for more info. */
""" + "\n\n" + content


generate_api_client(
    os.path.join(settings.BASE_DIR, "output", "api.ts"),
    csrf_token_variable_name="csrftoken",
    post_processor=post_processor,
    urlpatterns=urlpatterns)
