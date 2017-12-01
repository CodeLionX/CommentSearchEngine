import re

from cse.pipeline.Handler import Handler


class HtmlStopwordsHandler(Handler):

    __inlineJS = r"(?is)<(script|style).*?>.*?(</\1>)"
    __htmlComments = r"(?s)<!--(.*?)-->[\n]?"
    __tags = r"(?s)<.*?>"


    def __init__(self):
        pass


    def process(self, ctx, data):
        result = {}
        result["article_id"] = data["article_id"]
        result["article_url"] = data["article_url"]
        result["comments"] = {}
        for cid in data["comments"]:
            result["comments"][cid] = self.__cleanHtml(data["comments"][cid])

        ctx.write(result)


    def __cleanHtml(self, comment):
        """
        Copied from NLTK package.
        Remove HTML markup from the given string.

        :param html: the HTML string to be cleaned
        :type html: str
        :rtype: str
        """
        commentText = comment["comment_text"]
        # First we remove inline JavaScript/CSS:
        cleaned = re.sub(self.__inlineJS, "", commentText.strip())
        # Then we remove html comments. This has to be done before removing regular
        # tags since comments can contain '>' characters.
        cleaned = re.sub(self.__htmlComments, "", cleaned)
        # Next we can remove the remaining tags:
        cleaned = re.sub(self.__tags, " ", cleaned)
        # Finally, we deal with whitespace
        cleaned = re.sub(r"&nbsp;", " ", cleaned)
        cleaned = re.sub(r"  ", " ", cleaned)
        cleaned = re.sub(r"  ", " ", cleaned)
        comment["comment_text"] = cleaned
        return comment



class CtxHelper(object):
    
    def __init(self):
        pass
    
    def write(self, data):
        print(data["comments"]["someCid"]["comment_text"])



if __name__ == "__main__":
    data = {
        "article_url":"An URL",
        "article_id" : "An ID",
        "comments" : {
            "someCid": {
                "comment_author": "An Username",
                "comment_text" : """
<div class="description">
<ul class="blockList">
<li class="blockList">
<hr>
<br>
<pre>public class <span class="typeNameLabel">Logger</span>
extends <a href="http://docs.oracle.com/javase/7/docs/api/java/lang/Object.html?is-external=true" title="class or interface in java.lang">Object</a></pre>
<div class="block">This class allows us to isolate all our logging dependencies in one place. It also allows us to have zero runtime
 3rd party logging jar dependencies, since we default to JUL by default.
 <p>
 By default logging will occur using JUL (Java-Util-Logging). The logging configuration file (logging.properties)
 used by JUL will taken from the default logging.properties in the JDK installation if no <code>java.util.logging.config.file</code> system
 property is set.
 <p>
 If you would prefer to use Log4J or SLF4J instead of JUL then you can set a system property called
 <code>vertx.logger-delegate-factory-class-name</code> to the class name of the delegate for your logging system.
 For Log4J the value is <code>io.vertx.core.logging.Log4jLogDelegateFactory</code>, for SLF4J the value
 is <code>io.vertx.core.logging.SLF4JLogDelegateFactory</code>. You will need to ensure whatever jar files
 required by your favourite log framework are on your classpath.
 <p>
 Keep in mind that logging backends use different formats to represent replaceable tokens in parameterized messages.
 As a consequence, if you rely on parameterized logging methods, you won't be able to switch backends without changing your code.</div>
<dl>
<dt><span class="simpleTagLabel">Author:</span></dt>
<dd><a href="mailto:tim.fox@jboss.com">Tim Fox</a></dd>
</dl>
</li>
                """,
                "timestamp" : "The creation date",
                "parent_comment_id" : "some other comments id",
                "upvotes" : "Number of upvotes",
                "downvotes": "Number of downvotes"
            }
        }
    }
    handler = HtmlStopwordsHandler()
    ctx = CtxHelper()
    handler.process(ctx, data)
