#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="Truthcoin-POW",
    version="0.1",
    description="Truthcoin-in-Python",
    author="Zack Hess",
    author_email="<zack@dyffy.com>",
    maintainer="Zack Hess",
    maintainer_email="<zack@dyffy.com>",
    url="https://github.com/zack-bitcoin/Truthcoin-POW",
    install_requires=["numpy", "pyconsensus"],
    keywords = ["consensus", "prediction market", "PM", "truthcoin", "oracle"]
)
