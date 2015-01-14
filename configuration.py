'''
Written By Onur Demiralay
MIT License Copyright(c) 2015 Onur Demiralay
Github: @odemiral


Configuration class holds all the necessary configurations required by the db and Reddit Bot
Configuration object shared among all the dependend classes, changing these values will be enough to make
system-wide changes.
'''

import os

class Configuration(object):
    def __init__(self):
        #RedditBot Default values
        #It's a dummy password so don't try any funny business :)
        self.reddit_user_name = "username"
        self.reddit_password = "password"
        self.subreddits = "nottheonion+worldnews+Canada+UpliftingNews+philosophy"
        self.reddit_user_agent = "u/haikub0t Traditional 5-7-5 Haiku Generator"
        self.reddit_submission_limit = 100 #num of results to fetch.
        self.reddit_ignored_domains = ('reddit', 'imgur','twitter') #domains to be ignored when evaluating articles. In time this list will grow
        # self.reddit_comment_treshold = 100 #Treshold for num of comments in a reddit post, if it exceeds the treshold, don't bother submitting a comment.

        #DB Default values
        self.db_server = "localhost"
        self.db_port = 27017
        self.db_name = "HaikuBotDB"
        self.db_daemon_path = 'C:\\Program Files\\MongoDB 2.6 Standard\\bin\\'
        self.db_path = os.path.dirname(os.path.abspath(__file__)) + '\\db'
        self.db_proc_name = "mongod.exe"

        #Goose Default values
        self.use_meta_language = False
        self.target_language = 'en'
        self.enable_image_fetching = False
