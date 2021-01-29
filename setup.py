import setuptools

with open('README.md') as file:
    long_description = file.read()

setuptools.setup(
    name="drf-tsdk",
    version="0.1.0",
    url="https://github.com/ryan.laney/drf-tsdk",

    author="Ryan Laney",
    author_email="ryanlaney@gmail.com",

    description="A package to generate a TypeScript API client for Django Rest Framework views and viewsets.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['Django', 'Django Rest Framework',
              'DRF', 'Typescript', 'Python', 'API'],

    packages=['drf_tsdk'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',

    install_requires=[
        'django',
        'djangorestframework',
        'jsbeautifier'
    ]
)
