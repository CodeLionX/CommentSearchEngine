import argparse
import os

from cse.SearchEngine import SearchEngine
from cse.__init__ import __version__
from cse.__init__ import __title__

DIRECTORY = "data"
COMMENTSFILE = "comments.data"
AUTHORFILE = "authorMapping.data"
ARTICLEFILE = "articleMapping.data"


def read_queries(filename):
    if not os.path.exists(filename):
        raise ValueError("File {} does not exist!".format(filename))
    queries = []
    with open(filename, 'rt', encoding="UTF-8") as file:
        for line in file:
            queries.append(line)
    return queries


def main():
    # parse args
    parser = argparse.ArgumentParser(description='Search Engine for comments on news websites')
    parser.add_argument("query", help="a txt file with one boolean, keyword, phrase, ReplyTo, or Index query per line")
    parser.add_argument("--topN", help="the maximum number of search hits to be printed", type=int)
    parser.add_argument("--printIdsOnly", help="print only commentIds and not ids and their corresponding comments", action="store_true")
    args = parser.parse_args()

    # load queries
    shouldBuildIndex = False
    queries = read_queries(args.query)
    if queries and queries[0].lower().startswith("index:"):
        shouldBuildIndex = True
        queries = queries[1:]

    # output configuration:
    if args.printIdsOnly:
        print("printIdsOnly turned on")
    if shouldBuildIndex:
        print("shouldBuildIndex is True: first building index")
    if args.topN:
        print("Only returning topN={} results".format(args.topN))

    # call search engine
    cse = SearchEngine(
        DIRECTORY,
        COMMENTSFILE,
        ARTICLEFILE,
        AUTHORFILE
    )

    if shouldBuildIndex:
        cse.index()

    cse.loadIndex()
    for query in queries:
        cse.search(query, args.printIdsOnly)
    
    cse.close()


if __name__ == "__main__":
    main()