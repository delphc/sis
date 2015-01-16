#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sis
version = sis.__version__

setup(
    name='SIS',
    version=version,
    author='',
    author_email='delphine.colonna@gmail.com',
    packages=[
        'sis',
    ],
    include_package_data=True,
    install_requires=[
        'Django>=1.6.5',
    ],
    zip_safe=False,
    scripts=['sis/manage.py'],
)