from setuptools import setup

name = "drf-tsdk"
package = "drf_tsdk"
version = "0.1.0"
description = "A package to generate a TypeScript API client for Django Rest Framework views and viewsets."
url = "https://github.com/ryan.laney/drf-tsdk"
author = "Ryan Laney"
author_email = "ryanlaney@gmail.com"

with open("README.md", encoding="utf-8") as readme:
    long_description = readme.read()

with open("requirements.txt", encoding="utf-8") as fh:
    requirements = [
        r.strip() for r in fh.read().split("\n") if not r.strip().startswith("#")
    ]

setup(
    name=name,
    version=version,
    url=url,
    author=author,
    author_email=author_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["Django", "Django Rest Framework", "DRF", "Typescript", "Python", "API"],
    packages=[package],
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    python_requies=">=3.6",
    install_requires=requirements,
)
