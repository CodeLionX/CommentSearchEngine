"""
CSE - a web crawling and web searching application for news paper
comments written in Python

package for the replyTo index consisting of
 - dictionary for faster index access (term -> pointer, size)
 - main inverted index (pointer, size -> child comment ids)
 - delta inverted index (only needed during index creation: parent cid -> child comment cids)
"""