import argparse
import os

from cse.SearchEngine import SearchEngine
from cse.__init__ import __version__
from cse.__init__ import __title__

# This path is relativ to this python script
DIRECTORY = os.path.join(".")
# please specify the filenames of the raw comments data
COMMENTSFILE = "comments.csv"
AUTHORFILE = "authors.csv"
ARTICLEFILE = "articles.csv"


def checkIndexFilenames(filenameSource):
    commentsFilename = filenameSource.split(":")[1].strip()

    # check files
    for filename in [commentsFilename, AUTHORFILE, ARTICLEFILE]:
        if not os.path.exists(os.path.join(DIRECTORY, filename)):
            raise ValueError("File {} relative to this scripts directory could not be found!".format(os.path.join(DIRECTORY, filename)))

    return commentsFilename, AUTHORFILE, ARTICLEFILE


def read_queries(filename):
    if not os.path.exists(filename):
        raise ValueError("File {} does not exist!".format(filename))
    queries = []
    with open(filename, 'rt', encoding="UTF-8") as file:
        for line in file:
            queries.append(line)
    return queries


def print_results_to(results, filename, idsOnly=False):
    with open(filename, 'wt', encoding="UTF-8") as file:
        for res in results:
            if idsOnly:
                file.write(str(res) + "\n")
            else:
                file.write("{}, {}".format(res[0], res[1].replace("\n", "\\n")) + "\n")


def main():
    # parse args
    parser = argparse.ArgumentParser(description='Search Engine for comments on news websites')
    parser.add_argument("query", help="a txt file with one boolean, keyword, phrase, ReplyTo, or Index query per line")
    parser.add_argument("--topN", help="the maximum number of search hits to be printed", type=int)
    parser.add_argument("--printIdsOnly", help="print only commentIds and not ids and their corresponding comments", action="store_true")
    args = parser.parse_args()

    # load queries
    shouldBuildIndex = False
    commentsFile, authorFile, articleFile = COMMENTSFILE, AUTHORFILE, ARTICLEFILE
    if args.query.startswith("Index:"):
        shouldBuildIndex = True
        commentsFile, authorFile, articleFile = checkIndexFilenames(args.query)
        
    else:
        queries = read_queries(args.query)
        if queries and queries[0].startswith("Index:"):
            shouldBuildIndex = True
            commentsFile, authorFile, articleFile = checkIndexFilenames(queries[0])
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
        commentsFile,
        authorFile,
        articleFile
    )

    if shouldBuildIndex:
        cse.index()

    cse.loadIndex()
    for i, query in enumerate(queries):
        results = cse.search(query.strip(), idsOnly=args.printIdsOnly, topK=args.topN)
        print_results_to(results, "query{}.txt".format(i), idsOnly=args.printIdsOnly)

    cse.close()


if __name__ == "__main__":
    main()
