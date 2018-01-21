"""
CSE - a web crawling and web searching application for news paper
comments written in Python

index creation and using package, this package also deales with the index persistence
"""
import os
from cse.indexing.FileIndexer import FileIndexer
from cse.indexing.IndexReader import IndexReader
from cse.indexing.DocumentMap import DocumentMap
from cse.indexing.PostingList import PostingList
