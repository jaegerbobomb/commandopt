# -*- coding: utf-8 -*-
"""Commandopt setup file.

"""
from setuptools import setup, find_packages

from commandopt import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Commandopt",
    version=__version__,
    description="Turn a dict of arguments into cli commands, ideal companion of docopt.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaegerbobomb/commandopt",
    download_url="https://github.com/jaegerbobomb/commandopt/archive/v0.1.0.tar.gz",
    author="notmarrco",
    author_email="marrco@wohecha.fr",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.2'
)
