'''
Written By Onur Demiralay
MIT License Copyright(c) 2015 Onur Demiralay
Github: @odemiral

HaikuDB class, provides necessary functions to communicate with the DB.
if mongod instance is not running, it will automatically look for it in the path defined in configuration.py

Please check the configuration.py if you want to change any of the default settings.
'''
import pymongo
from pymongo import errors

import configuration
import subprocess
import time
import psutil


from bson.objectid import ObjectId
'''
Currently Document in DB consist of
    {   id: submissionID,
        url: submissionURL,
        haiku: submittedHaiku,                     #Reddified format
        timestamp: submissionTimeStamp             #YYYY-MM-DD HH:MM:SS
    }
'''

'''
BUG! DB WENT IN TO INFINTE LOOP WHEN IT WAS RUNNING!
FIND OUT WHY!
'''
class HaikuDB(object):
    def __init__(self, config=None):
        self.config = config or configuration.Configuration()
        self.extend_config()
        self.initialize()

    def initialize(self):
        self.dbStart()
        try:
            self.mongoDB = pymongo.MongoClient(self.config.db_server, self.config.db_port)[self.config.db_name]
        except pymongo.errors.ConnectionFailure as e:
            print("Error! Failed To Connect To Database: " + e.message)
            self.dbShutdown()
            exit(-1)

    '''
    Starts the db using  with current path to mongodb daemon
    Returns True if the db is already running or was able to start the db, False otherwise
    Note: to change the path to db, either change the value and pass it as config in the constructor, or change the
    default value in configuration.py
    change mongod.exe to ./mongod if you're running it in a unix system
    change options to pass more options to mongodb daemon
    '''
    def dbStart(self, options="--dbpath", exe="mongod.exe"):
        isStarted = True
        exePath = self.config.db_daemon_path + exe
        args = [exePath, options, self.config.db_path]

        isDBRunning = self.isMongoRunning()
        returnCode = 100 #Default unhandled exception code for MongoDB

        '''
        if it's not Running, then start the db, and get the returnCode
        '''
        if not isDBRunning:
            mongoProcess = subprocess.Popen(args, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
            time.sleep(3) #sleep 3 sec, it's more than enough time to check if mongodb has starterd.
            returnCode = mongoProcess.poll()
             #print(mongoProcess.poll())

        #DB is not running and return code is not None, then there must be an error opening the db, try to repair it
        if isDBRunning or returnCode is None:
            print("isDBRunning?",isDBRunning)
            isStarted = True

        elif not isDBRunning and returnCode is not None:
            print("Repairing it")
            returnCode = self.dbRepair()
            if returnCode is not None or returnCode != 0:
                print("Error! Failed to Repair Database, Please Run Mongo Daemon Manually And Try Again")
                exit(100)
        else:
            print("Failed to Start Database, Please Run Mongo Daemon Manually And Try Again")
            exit(100)

        return isStarted

    '''
    Tries to Repair the database by using --repair option for Mongo Daemon
    Returns 0 or None on Success, on fail, it reutrns the corresponded error code
    which is most likely going to be 100 since it's the unhandeled error code for Mongo Daemon
    '''
    def dbRepair(self, options=("--repair", "--dbpath"), exe=None):
        if exe is None:
            exe = self.config.db_proc_name

        exePath = self.config.db_daemon_path + exe
        args = [exePath, options[0], options[1], self.config.db_path]
        #print(args)
        mongoProcess = subprocess.Popen(args, stderr=subprocess.PIPE)
        # time.sleep(5) #sleep 5 sec, it's more than enough time to check if mongodb has starterd.
        outStream = mongoProcess.communicate()[0]
        returnCode = mongoProcess.poll()
        #print("Return Code After Repair: ", returnCode)
        return returnCode

    '''
    Checks if the server is still running, if it does, it shuts it down.
    According to tutorials, this is the safe and clean way of shutting down the server
    http://docs.mongodb.org/manual/reference/method/db.shutdownServer/#db.shutdownServer
    '''

    def dbShutdown(self, options="--shell", exe="mongo.exe"):
        #isStarted = True
        exePath = self.config.db_daemon_path + exe
        args = [exePath, options]
        #print(args)
        print "###################################################################"
        print "## Shutting down db"

        isDBRunning = self.isMongoRunning()
        #If it's running, shutdown the server
        if isDBRunning:
            mongoProcess = subprocess.Popen(args, stdin = subprocess.PIPE)
            mongoProcess.stdin.write("use admin\n")
            mongoProcess.stdin.write("db.shutdownServer()\n")
            outStream = mongoProcess.communicate()[0]
        print "###################################################################"

    '''
    Uses psutil to iterate through process currently running to check if mongodb is running in the background
    '''
    def isMongoRunning(self):
        isRunning = False
        for proc in psutil.process_iter():
            try:
                if proc.name() == self.config.db_proc_name:
                    isRunning = True
                    break
            except psutil.AccessDenied as e:
                pass
                #print "Access denied on process"
        return isRunning

    '''
    This will delete the database permanently, use it with caution!
    Since we're only using 1 collection as DB, it actually deletes the collection.
    '''
    def deleteDB(self):
        self.mongoDB.connection.drop_database(self.config.db_name)
    '''
    Check if config is a dictionary, if it is then config consist non-default values,
    find and change all the variables to non-default values.
    '''
    def extend_config(self):
        if isinstance(self.config, dict):
            # print("isinstance!")
            config = configuration.Configuration()
            for i, j in self.config.items():
                print(i,j)
                if hasattr(config, i):
                    setattr(config, i, j)
            self.config = config

    '''
    insert dictionary onto the database.
    Please check the header to see what elements dic consists of.
    '''
    def insert(self, dic):
        # self.mongoDB.collection.insert(dic)
        try:
            self.mongoDB.collection.insert(dic)
        except pymongo.errors.OperationFailure as e:
            print("Error: Failed to insert to Database, ",e)
            self.dbShutdown()
            exit(-1)
    '''
    Returns the number of documents in the collection.
    Since haikuDB only uses a single collection, this will return # elements in the db
    '''
    def getSize(self):
        return self.mongoDB.collection.count()

    '''
    Given id, find if the document exist in the database.
    The key difference between isExist and find is that, isExist is much faster since we don't need to read and return the actual document, all we need is a cursor,
    return true if document specified by id exist (using count on cursor object), false otherwise
    More info on performance can be found here: https://blog.serverdensity.com/checking-if-a-document-exists-mongodb-slow-findone-vs-find/
    '''
    def isExist(self, id):
        isFound = False
        #print self.mongoDB.collection.find({'id': id}).limit(1)
        if self.mongoDB.collection.find({'id': id}).limit(1).count() != 0:
            isFound = True
        return isFound
        # return self.mongoDB.collection.find({'id': id}).limit(1)

    '''
    given id finds and returns the document
    It retruns None if the document doesn't exist.
    '''
    def find(self, id):
        # return self.mongoDB.collection.find_one({'id': id})
        return self.mongoDB.collection.find_one({'id': id})

