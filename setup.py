#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from io import open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version('django_swagger_utils', '__init__.py')

if sys.argv[-1] == 'publish':
    try:
        import wheel
        print(("Wheel version: ", wheel.__version__))
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    required = f.read().splitlines()



setup(
    name='django-swagger-utils',
    python_requires='>=3.7',
    version=version,
    description="""Automate API generation from swagger""",
    long_description=readme + '\n\n' + history,
    author='Lokesh Dokara',
    author_email='lokesh@ibtspl.com',
    url='https://github.com/eldos-dl/django-swagger-utils',
    packages=[
        'django_swagger_utils',
    ],
    include_package_data=True,
    install_requires=required,
    zip_safe=False,
    keywords='django-swagger-utils',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
