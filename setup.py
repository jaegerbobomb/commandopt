# -*- coding: utf-8 -*-
"""Commandopt setup file.

"""
from setuptools import find_packages, setup

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
    download_url="https://github.com/jaegerbobomb/commandopt/archive/v0.4.0.tar.gz",
    author="notmarrco",
    author_email="marc@maj44.com",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    # commandopt accepts any dict of arguments, so the argument parser is an
    # optional companion rather than a hard requirement. docopt-ng is the
    # maintained, drop-in replacement for the original (unmaintained) docopt.
    extras_require={
        "docopt": ["docopt-ng>=0.9"],
        "test": ["pytest", "docopt-ng>=0.9"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
