import os

from django.urls import include, path
from django.conf import settings

from drf_tsdk import generate_typescript_bindings

urlpatterns = [
    path("api/v1/", include("api.urls")),
]


def post_processor(content):
    return (
        """// @ts-nocheck
/* eslint-disable */

/** This file was generated automatically by drf-tsdk.
* It should be in .gitignore, and you should not edit it;
* its contents will be overwritten automatically every time
* the Django server is run. See https://github.com/ryan.laney/drf-tsdk
* for more info. */
"""
        + "\n\n"
        + content
    )


generate_typescript_bindings(
    os.path.join(settings.BASE_DIR, "output", "api.ts"),
    csrf_token_variable_name="csrftoken",
    post_processor=post_processor,
    urlpatterns=urlpatterns,
)
