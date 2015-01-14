'''
Written By Onur Demiralay
MIT License Copyright(c) 2015 Onur Demiralay
Github: @odemiral


Haiku class is responsible for generating Haikus. You can easily use this class on its own by passing string to the constructor.

'''
from collections import defaultdict
import re
import random
import sys

'''
Lots of room for improvement,
Implement a grammar checker to generate grammatically correct haikus
Instead of heuristical approach, implement a dictionary of words in english to get syllable count instead.

'''
class Haiku:
    def __init__(self,str):
        self.str = str
        self.multimap = defaultdict(list)
        self.haikuList = None #store each line of haiku as an element of the list.
        self.formatStr()
        #self.generateHaiku()


    #main function, that generates a 5-7-5 haiku
    def generateHaiku(self):
        self.constructMultiMap()
        try:
            firstLine = self.generateLines(5)
            secondLine = self.generateLines(7)
            thirdLine = self.generateLines(5)
            self.haikuList = [firstLine, secondLine, thirdLine]
        except ValueError as e:
            self.haikuList = []
        #print self.haikuList
        #haiku = self.constructHaiku(firstLine, secondLine, thirdLine)
        #return haiku

    '''
    Return haiku in a list format. This function must be called after generateHaiku.
    '''
    def getHaikuList(self):
        return self.haikuList

    '''
    Converts Haiku List to str.
    if Haiku List is empty, then return an empty string
    '''
    def getHaikuStr(self):
        haikuStr = ""
        if self.haikuList:
            haikuStr = self.constructHaiku(self.haikuList[0], self.haikuList[1], self.haikuList[2])
        return haikuStr

    '''
    Simple, yet accurate heuristic approach to count syllables.
    1 syllable per vowel assuming it satisfies following conditions:
        #don't count suffixes that end with -es -ed -e
        #consecutive vowels only counts as one
    TODO: Improve accuracy, and implement dictionaries to support other languages as well.
    '''
    def countSyllables(self, word):
        #find words ending with laeiouy, es, ed or e
        pattern = r'(?:[^laeiouy]es|ed|[^laeiouy]e)$'
        word = re.sub(pattern, "", word) #replace every occurence of above pattern.
        word = re.sub(r'^y', "", word)
        pattern = r'[aeiouy]{1,2}' #find occurences with 1-2 consecutive vowels, queueing will return 3, ue, ue, i
        res = re.findall(pattern, word) #using findall for /g
        return len(res)

    '''
    Constructs a list with words with syllables sum to syllableLimits
    '''
    def generateLines(self, syllableLimits):
        wordArr = []
        while(syllableLimits != 0):
            try:
                word, syllable = self.pickRandomWord(syllableLimits)
                syllableLimits = syllableLimits - syllable
                #print("found: ", word, "with", syllable, "syllables")
                wordArr.append(word)
            except ValueError as e:
                raise ValueError

        return wordArr

    '''
    Formats str to get rid of special characters and split it to whitespace delimited list.
    transforms self.str to list.
    '''
    def formatStr(self):
        pattern = re.compile("[^\w\']") #unicode friendly
        self.str = pattern.sub(' ', self.str)
        self.str = self.str.lower()
        self.str = self.str.split()

    '''
    Constructs MultiMap like structure where value is a list of words and key is the number of syllables in those words.
    ex: multimap[3] = [potato, lunatic, absolute, determine]
    words must have at least 1 syllables (no white spaces, digits, special chars) and it must be consist of at least 2 letters
    except for word 'I'
    '''
    def constructMultiMap(self):
        for word in self.str:
            syllables = self.countSyllables(word)
            #print(word)
            if (syllables >= 1) and (len(word) >= 2 or word == 'I'):
                self.multimap[syllables].append(word)

    '''
    concats all the lines and beutifies the final string.
    Currently not used by the redditBot
    '''
    def constructHaiku(self, firstLine, secondLine, thirdLine):
        haiku = ""
        for word in firstLine:
            haiku += word + ' '
        haiku += '\n'
        for word in secondLine:
            haiku += word + ' '
        haiku += '\n'
        for word in thirdLine:
            haiku += word + ' '
        return haiku

    #find a word by iterating through every element in the list
    def bruteForceFindWord(self, syllableSize):
        possibleWords = None
        #key = None
        for key in self.multimap:
            if key <= syllableSize:
                #print("KEY:",key)
                #print(self.multimap[key])
                possibleWords = self.multimap[key]
                syllableSize = key
                break
                # return possibleWords, key
                # for val in self.multimap[key]:
                #     print("VAL:",val)
                #     print("KEY:",key)
                #     print(self.multimap[key])
                #     #word = val
                #     #syllableSize = key
                #     #check if the word is already in haiku, if it is then continue, if not use it.
                #     return word,key
        # print("returning", possibleWords, "and", syllableSize)
        return possibleWords,syllableSize

    '''
    Given syllableSize, fetches a random word from multimap that has equal or less syllables than syllableSize
    after some tries, if it can't find words randomly it will find one by calling bruteForceFindWord function.
    If there are enough words in the multimap, calling bruteForceFindWord will be an unlikely possibility.
    You can always assume that this function will either terminate the program or return a word, no further
    error handling need to be done
    TODO: Poor Error handling, revise it so that it doesn't interrupt the flow of the program.
    '''
    def pickRandomWord(self, syllableSize):
        rndSize = random.randint(1,syllableSize)
        #print("@@@@RANDSIZE: ", rndSize)
        possibleWords = self.multimap[rndSize]
        loopCounter = 0 #keep tracks of how many times tried to find a word randomly
        loopLimit = 1000 # limit of how many times it should try to find a word randomly before switching to iterative mode
        while (not possibleWords and (loopCounter != loopLimit)):
            rndSize = random.randint(1,syllableSize)
            possibleWords = self.multimap[rndSize]
            loopCounter += 1
        if not possibleWords:
            print("Trying brute force")
            possibleWords,rndSize = self.bruteForceFindWord(syllableSize)
            if not possibleWords:
                print("Not enough word combinations exist to generate a Haiku :(")
                raise ValueError
                #sys.exit(-1)
        syllableSize = rndSize
        rndPos = random.randint(0, len(possibleWords) - 1)
        # print("possibleWords[rndPos]:", possibleWords[rndPos], "syllableSize:", syllableSize)
        return possibleWords[rndPos], syllableSize
