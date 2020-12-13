import os
import setuptools

with open('README.md') as file:
    long_description = file.read()

setuptools.setup(
    name="drf-typescript-api-client",
    version="0.1.0",
    url="https://github.com/ryan.laney/drf-typescript-api-client",

    author="Ryan Laney",
    author_email="ryanlaney@gmail.com",

    description="A package to generate a TypeScript API client for Django Rest Framework views and viewsets.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['Django', 'Django Rest Framework',
              'DRF', 'Typescript', 'Python', 'API'],

    packages=['drf_typescript_api_client'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',

    install_requires=[
        'django',
        'djangorestframework',
        'jsbeautifier'
    ]
)
