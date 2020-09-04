#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup
import sys

HERE_PATH = os.path.abspath(os.path.dirname(__file__))


# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()


ABOUT = {}
with open(os.path.join(HERE_PATH, 'pgark', '__about__.py'), 'r') as f:
    exec(f.read(), ABOUT)

with open('README.md', 'r') as f:
    README = f.read()

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

setup(
    name=ABOUT['__title__'],
    version=ABOUT['__version__'],
    description=ABOUT['__description__'],
    author=ABOUT['__author__'],
    author_email=ABOUT['__author_email__'],
    url=ABOUT['__url__'],

    long_description=README,
    long_description_content_type='text/markdown',

    packages=('pgark',),
    include_package_data=True,

    python_requires=">=3.6",

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
        'Project': 'https://www.github.com/dannguyen/pgark',
        'Source': 'https://www.github.com/dannguyen/pgark',
        'Tracker': 'https://www.github.com/dannguyen/pgark/issues'
    }
)
