#!/usr/bin/env python
# coding: utf-8
"""Minimal setup."""

import os
import re
from setuptools import setup, find_packages

PROJECT = 'cframe'


def get_property(prop, project):
    """Get certain property from project folder."""
    with open(os.path.join(project, '__init__.py')) as f:
        result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop),
                           f.read())
    return result.group(1)


with open('requirements.txt') as f:
    REQS = f.read().splitlines()


setup(name=PROJECT,
      install_requires=REQS,
      version=get_property('__version__', PROJECT),
      description='Framework for design of prediction-based compression methods',
      author='Ugur Cayoglu',
      setup_requires=["pytest-runner"],
      tests_require=["pytest"],
      package_data={PROJECT:['data/*']},
      author_email='cayoglu@kit.com',
      packages=find_packages(),
      )
