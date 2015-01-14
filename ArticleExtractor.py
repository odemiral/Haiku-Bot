'''
Written By Onur Demiralay
MIT License Copyright(c) 2015 Onur Demiralay
Github: @odemiral

Article Extractor, given article, ArticleExtractor object calls extractArticle class to extract data (image,text,etc) from HTML pages

'''
from goose import Goose
import urllib2
import configuration

class ArticleExtractor(object):
    def __init__(self,config=None):
        self.config = config or configuration.Configuration()
        self.extend_config()
        self.gooseObj = Goose(config)

    '''
    Given url, it extracts the body of the article, and returns the string.
    It returns None or empty string if it fails to extract the article.
    If the article's domain is in ignored domains, then it doesn't extract the article and returns None
    '''
    def extractArticle(self,url):
        articleStr = None
        ##handle HTTP & URL Errors by skipping articles
        try:
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            opener.addheaders = [('User-agent', self.config.reddit_user_agent)]
            response = opener.open(url)
            raw_html = response.read()
            #handle cases where Goose throws ValueError or IOError when parsing (happens when Goose confuses scripts with images.
            try:
                article = self.gooseObj.extract(raw_html=raw_html)
                articleStr = article.cleaned_text
            except (ValueError, IOError) as e:
                print("Can't parse the article, moving onto the next one.")
        except urllib2.HTTPError as e:
            print "HTTP Error! " + str(e.code)
        except urllib2.URLError as e:
            print "URL Error! " + str(e.args)

        return articleStr


    '''
    Check if config is a dictionary, if it is then config consist non-default values,
    find and change all the variables to non-default values.
    '''
    def extend_config(self):
        if isinstance(self.config, dict):
            print("isinstance!")
            config = configuration.Configuration()
            for i, j in self.config.items():
                print(i,j)
                if hasattr(config, i):
                    setattr(config, i, j)
            self.config = config


