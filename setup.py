"""Python setup.py for aflight package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="aflight",
    version=read("aflight", "VERSION"),
    description="Arrow Flight simple API service",
    url="https://github.com/pkit/aflight/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Constantine Peresypkin",
    packages=find_packages(exclude=["example", "tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
    extras_require={"test": read_requirements("requirements-test.txt")},
    entry_points={
        "console_scripts": ["aflight = aflight.__main__:main"]
    },
)
