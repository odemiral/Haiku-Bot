'''
Written By Onur Demiralay
MIT License Copyright(c) 2015 Onur Demiralay
Github: @odemiral

Haiku Bot for Reddit capable generating haiku's based on the words extracted and posts them on Reddit.
It uses MongoDB to store previously generated haikus. If you want more information, please check the documentation for each function.

Note: I'm aware mongoDB is an overkill for a bot like this, but I thought this could be a great opportunity to learn it.
Feel free to send me an e-mail if you have any suggestions or improvements :)
'''

import praw
import sys
from urlparse import urlparse
from datetime import datetime
from time import time, sleep

from HaikuDB import HaikuDB
from Haiku import Haiku
from ArticleExtractor import ArticleExtractor
import configuration

'''
You might wanna overwrite configuration.py to change reddit_user_name and reddit_password if you ever want to run it yourself.
'''
class RedditBot(object):
    def __init__(self,config=None):
        self.config = config or configuration.Configuration()
        self.extend_config()

        self.haikuDB = HaikuDB(config) ##Start the database
        print "DB SIZE: " + str(self.haikuDB.getSize())
        self.articleExtractor = ArticleExtractor(config)

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


    '''
    Based on config.reddit_submission_limit, return current hot submissions for subreddits specified in config.subreddits
    TODO: this function bound to throw HTTP 4xx errors (most likely 429) Make sure you handle HTTP Errors
    TODO: Make sure you delete submissions linking to non-news sites such as imgur, and reddit.com
    '''
    def getSubmissions(self):
        submissions = []

        try:
            r = praw.Reddit(user_agent = self.config.reddit_user_agent)
            r.login(self.config.reddit_user_name, self.config.reddit_password)
            submissions = r.get_subreddit(self.config.subreddits).get_hot(limit = self.config.reddit_submission_limit)
        except praw.errors.InvalidUserPass as e:
            print "ERROR: " + e.message + ", make sure your login info is correct!"

        return submissions #r.get_subreddit(self.config.subreddits).get_hot(limit = self.config.reddit_submission_limit)


    '''
    Checks if url is in ignored domains, if it is, returns True, False otherwise.
    '''
    def isInIgnoredDomain(self,url):
        inIgnoredDomain = False
        for domain in self.config.reddit_ignored_domains:
            if domain in urlparse(url).netloc:
                inIgnoredDomain = True
                break
        return inIgnoredDomain


    '''
    Check if the current submission id is in database,
    if it is, then the article is already submitted so, no need to submit it again.
    '''
    def isItSubmitted(self,id):
        return self.haikuDB.isExist(id)


    '''
    Try to submit a comment, which contains haiku to reddit
    Then insert the submission into the database

    if haiku list is empty, then don't submit it
    '''
    def submitHaiku(self, submission, haiku):
        isRateLimitPassed = True
        timestamp = None
        while isRateLimitPassed:
            print "trying..."
            try:
                response = submission.add_comment(haiku)
                timestamp = datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
                print(timestamp)
                isRateLimitPassed = False
                print isRateLimitPassed
            except praw.errors.RateLimitExceeded as e:
                print e
                print e.sleep_time
                isRateLimitPassed = True
                sleep(e.sleep_time) #Sleep until the ratelimit passes

        dbDic = {   'id'        :   submission.id,
                    'url'       :   submission.url,
                    'haiku'     :   haiku,
                    'timestamp' :   timestamp
                }
        print submission.url
        self.haikuDB.insert(dbDic)

    '''
    Main function, searches reddit for submissions, for each submissions, that's not in the database and the domain of the submission is not ignored,
    it extracts the article, and generates haiku based on the words within the article, it then inserts submission url, id, haiku, and timestamp to prevent processing the same
    articles in the future.

    Note: if Goose fails to extract articles, extractArticle will return an empty list or None, and the bot won't try to generate haikus on articles with no list
    If there are simply not enough words to generate a haiku in an article, it simply skips the article.
    TODO:
    '''
    def start(self):
        # haikusDebugging = []
        print "getting submissions..."
        submissions = self.getSubmissions()
        for submission in submissions:
            submissionURL = submission.url
            submissionID = submission.id
            print str(submissionURL) + " " + str(submissionID)
            print self.isInIgnoredDomain(submissionURL)
            print self.isItSubmitted(submissionID)
            #Check if you're willing to extract the article
            if not self.isInIgnoredDomain(submissionURL) and not self.isItSubmitted(submissionID):
                article = self.articleExtractor.extractArticle(submissionURL)
                #print(article)
                if article: #not None or empty str
                    myhaiku = Haiku(article)
                    myhaiku.generateHaiku()
                    haikuL = myhaiku.getHaikuList()
                    if haikuL: #if list is not empty:
                        reddifiedHaiku = self.reddify(haikuL)
                        self.submitHaiku(submission,reddifiedHaiku)
                        # haikusDebugging.append(reddifiedHaiku)
        # saveHaikusToFile(haikusDebugging)

    '''
    Reconstructs the haiku to make it look more appealing on Reddit (uses Markdown Format)
    '''
    def reddify(self, haiku):
        header = "**Haiku of the Post**"
        redHaiku = "* * * \n\n"
        for line in haiku:
            redLine = "*"
            for word in line:
                redLine += word + " "
            redLine = redLine[:-1] + "* \n\n"
            redHaiku += redLine
        footNote = "* * * \n\n ***written by a bot*** / ***not always the best results*** / ***but it will get better***"
        return header + "\n" + redHaiku + footNote


#USED ONLY FOR DEBUGGING PURPOSES!
def saveHaikusToFile(haikus):
    with open("haikus.txt", 'w') as f:
        for haiku in haikus:
            f.write(haiku)
            f.write("\n")
    print("haikus saved")



def main(argv):
    #Un coment this part if you want to flush the database.
    # myDB = HaikuDB()
    # myDB.deleteDB()
    #you can overwrite default values by passing a dictionary with new values like this
    redditBot = RedditBot({'reddit_submission_limit': 20,
                           'reddit_user_name': 'your_user_name_goes_here',
                           'reddit_password': 'your_password_goes_here',
                           'subreddits:':'UpliftingNews'})
    redditBot.start()
    redditBot.haikuDB.dbShutdown() #Shutdown the db safely.
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
