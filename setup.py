#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='pgark',
    version='0.0.1',
    description='Python library and CLI for archiving URLs on popular services like Wayback Machine',
    long_description=read('README.rst'),
    author='Dan Nguyen',
    author_email='dansonguyen@gmail.com',
    url='https://www.github.com/dannguyen/pgark',
    packages=('pgark',),
    include_package_data=True,
    license="MIT",
    install_requires=[
        'requests>=2.20.0',
        'click'
    ],
    entry_points='''
        [console_scripts]
        pgark=pgark.cli:main
    ''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License'
    ],
    project_urls={
        'Project': 'http://www.pastpages.org/',
        'Source': 'https://www.github.com/dannguyen/pgark',
        'Tracker': 'https://www.github.com/dannguyen/pgark/issues'
    }
)
