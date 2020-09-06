#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup
import sys

ABOUT = {}
HERE_PATH = os.path.abspath(os.path.dirname(__file__))

# deprecated by `make ship`
# # 'setup.py publish' shortcut.
# if sys.argv[-1] == "publish":
#     os.system("python setup.py sdist bdist_wheel")
#     os.system("twine upload dist/*")
#     sys.exit()


with open(os.path.join(HERE_PATH, "pgark", "__about__.py"), "r") as f:
    exec(f.read(), ABOUT)

with open("README.md", "r") as f:
    README = f.read()

setup(
    extras_require={
        "dev": [
            "appdirs==1.4.4",
            "attrs==20.2.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "black==20.8b1",
            "bleach==3.1.5; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
            "certifi==2020.6.20",
            "chardet==3.0.4",
            "click==7.1.2",
            "colorama==0.4.3; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
            "coverage==5.2.1",
            "docutils==0.16; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
            "freezegun==1.0.0",
            "idna==2.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "iniconfig==1.0.1",
            "keyring==21.4.0; python_version >= '3.6'",
            "more-itertools==8.5.0; python_version >= '3.5'",
            "mypy-extensions==0.4.3",
            "packaging==20.4; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "pathspec==0.8.0",
            "pkginfo==1.5.0.1",
            "pluggy==0.13.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "py==1.9.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "pygments==2.6.1; python_version >= '3.5'",
            "pyparsing==2.4.7; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "pytest==6.0.1",
            "python-dateutil==2.8.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "readme-renderer==26.0",
            "regex==2020.7.14",
            "requests==2.24.0",
            "requests-toolbelt==0.9.1",
            "responses==0.12.0",
            "rfc3986==1.4.0",
            "six==1.15.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "toml==0.10.1",
            "tqdm==4.48.2; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
            "twine==3.2.0",
            "typed-ast==1.4.1",
            "typing-extensions==3.7.4.3",
            "urllib3==1.25.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'",
            "webencodings==0.5.1",
            "wheel==0.35.1",
        ]
    },
    name=ABOUT["__title__"],
    version=ABOUT["__version__"],
    description=ABOUT["__description__"],
    author=ABOUT["__author__"],
    author_email=ABOUT["__author_email__"],
    url=ABOUT["__url__"],
    long_description=README,
    long_description_content_type="text/markdown",
    packages=("pgark",),
    include_package_data=True,
    python_requires=">=3.6",
    setup_requires=["pipenv-setup"],
    install_requires=[
        "certifi==2020.6.20",
        "chardet==3.0.4",
        "click==7.1.2",
        "colorama==0.4.3; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "commonmark==0.9.1",
        "cssselect==1.1.0",
        "idna==2.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "lxml==4.5.2",
        "pygments==2.6.1; python_version >= '3.5'",
        "requests==2.24.0",
        "rich==6.0.0",
        "typing-extensions==3.7.4.3",
        "urllib3==1.25.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'",
    ],
    entry_points="""
        [console_scripts]
        pgark=pgark.cli:main
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    project_urls={
        "Project": "https://www.github.com/dannguyen/pgark",
        "Source": "https://www.github.com/dannguyen/pgark",
        "Tracker": "https://www.github.com/dannguyen/pgark/issues",
    },
)
