#!/usr/bin/env python

from setuptools import setup

setup(
    name='CommentSearchEngine',
    version='0.1.0',
    description='Search Engine for Comments at news websites',
    author='Benedikt Bock, Sebastian Schmidl',
    author_email='mail@benedikt1992.de, sebastian.schmidl@t-online.de',
    url='https://github.com/CodeLionX/CommentSearchEngine',
    license='MIT',
    # packages
    packages=['cse'],

    # dependencies
    install_requires=['scrapy>=1.4.0'],

    # specific files to install
    package_data={'testCrawlerData': ['testData.csv']},
    #data_files=[('myfile': 'folder/file')],

    # executable scripts
    entry_points={
        'console_scripts': [
            'crawl=cse.crawler.crawler:main'
        ],
    },
)