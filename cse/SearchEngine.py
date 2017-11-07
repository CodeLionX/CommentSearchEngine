class SearchEngine():

    def index(self, directory):
        pass

    def loadIndex(self, directory):
        pass

    def search(self, query):
        results = []
        return results

    def printAssignment2QueryResults(self):
        print searchEngine.search("October")
        print searchEngine.search("jobs")
        print searchEngine.search("Trump")
        print searchEngine.search("hate")

searchEngine = SearchEngine()
searchEngine.printAssignment2QueryResults()