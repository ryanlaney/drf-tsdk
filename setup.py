from setuptools import setup

NAME = "drf-tsdk"
PACKAGE = "drf_tsdk"
VERSION = "0.1.0"
DESCRIPTION = "A package to generate a TypeScript API client for Django Rest Framework views and viewsets."
URL = "https://github.com/ryan.laney/drf-tsdk"
AUTHOR = "Ryan Laney"
AUTHOR_EMAIL = "ryanlaney@gmail.com"

with open("README.md", encoding="utf-8") as readme:
    long_description = readme.read()

with open("requirements.txt", encoding="utf-8") as fh:
    requirements = [
        r.strip() for r in fh.read().split("\n") if not r.strip().startswith("#")
    ]

setup(
    name=NAME,
    version=VERSION,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["Django", "Django Rest Framework", "DRF", "Typescript", "Python", "API"],
    packages=[PACKAGE],
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    python_requires=">=3.6",
    install_requires=requirements,
)
