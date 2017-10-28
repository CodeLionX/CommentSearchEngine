#!/usr/bin/env python

import os
from setuptools import setup

with open(os.path.join('cse', 'VERSION')) as version_file:
    version = version_file.read().strip()

setup(
    name='CommentSearchEngine',
    version=version,
    description='Search Engine for Comments at news websites',
    author='Benedikt Bock, Sebastian Schmidl',
    author_email='mail@benedikt1992.de, sebastian.schmidl@t-online.de',
    url='https://github.com/CodeLionX/CommentSearchEngine',
    license='MIT',

    # dependencies
    install_requires=[
        'scrapy>=1.4.0',
        'cffi>=1.7'
    ],

    # packages
    packages=['cse'],
    package_dir={'cse': './cse'},
    package_data={'cse': ['./VERSION', '../LICENSE']},
    include_package_data=True,

    # executable scripts
    entry_points={
        'console_scripts': [
            'crawl=scripts.crawl:main'
        ],
    },
)