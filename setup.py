#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="pyconsensus",
    version="0.1",
    description="Even-more-experimental implementation of Truthcoin",
    author="Zack Hess",
    author_email="<zack@dyffy.com>",
    maintainer="Zack Hess",
    maintainer_email="<zack@dyffy.com>",
    url="https://github.com/tensorjack/skunkworks",
    packages=["skunkworks"],
    install_requires=["numpy", "pyconsensus"],
    keywords = ["consensus", "prediction market", "PM", "truthcoin", "oracle"]
)
