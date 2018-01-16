"""
CSE - a web crawling and web searching application for news paper
comments written in Python

package for the default inverted posting lists index consisting of
 - dictionary for faster index access (term -> pointer, size)
 - main inverted index (pointer, size -> posting list)
 - delta inverted index (only needed during index creation: term -> posting list)
"""