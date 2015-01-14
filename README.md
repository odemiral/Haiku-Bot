Haiku Bot for Reddit
====================
A [Haiku](https://en.wikipedia.org/wiki/Haiku) bot capable of generating haikus by extracting data from articles posted on Reddit. It submits the result in the form of a comment.

How to Run
----------
Running ReditBot.py will automate the whole process for you, but before you do that you will have to provide a reddit username & password. You can do this by either changing default values in **configuration.py** or pass them to RedditBot constructor as a dictionary like this:

        redditBot = RedditBot({'reddit_submission_limit': 200,
                           'reddit_user_name': 'your_user_name_goes_here',
                           'reddit_password': 'your_password_goes_here',
                           'subreddits:':'UpliftingNews'})

The bot uses MongoDB to prevent resubmitting haikus that are already generated. It looks for the database in db/ folder, if you don't have mongod instance running, it will automatically start one for you.

Dependencies
------------
[python-goose 1.0.22](https://github.com/grangier/python-goose/tree/1.0.22) (Newer versions tend to cause problems)

[praw](https://github.com/praw-dev/praw)

[PyMongo](https://github.com/mongodb/mongo-python-driver)

License
-----------------
MIT License


Generated Samples
-------------
[Original Article](http://wric.com/2014/12/22/christmas-cheer-high-schooler-gives-classmates-new-sneakers/)
![Haiku Sample 1](https://dl.dropbox.com/s/xmgp1sfckwmzddp/Sample1.JPG)

[Original Article](http://www.thewrap.com/cbs-sports-radio-host-jim-rome-calls-college-marching-band-members-dorks-on-twitter-apologizes/)
![Haiku Sample 2](https://dl.dropbox.com/s/1ydcj541qc2yapb/Sample2.JPG)

[Original Article](http://www.washingtonpost.com/blogs/wonkblog/wp/2014/12/26/chicago-gave-hundreds-of-high-risk-kids-a-summer-job-violent-crime-arrests-plummeted/)
![Haiku Sample 3](https://dl.dropbox.com/s/tzafvjla06x2s0e/Sameple3.JPG)
