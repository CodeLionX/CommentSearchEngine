"""
CSE - a web crawling and web searching application for news paper
comments written in Python
"""
import os

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version_file:
    version = version_file.read().strip()
del os

__title__ = 'CommentSearchEngine'
__version__ = version
__author__ = 'Benedikt Bock, Sebastian Schmidl'
__license__ = 'MIT'

# top-level shortcuts
from .CommentSpider import CommentSpider 