# -*- coding: utf-8 -*-
"""
Created on Tue May 22 15:47:09 2018

@author: 20166843
"""
import access
import pandas as pd
import numpy as np

database = access.db
conversationList = []

airlines_id = ["56377143", "106062176", "18332190", "22536055", "124476322", "26223583", "2182373406", "38676903",
               "1542862735", "253340062", "218730857", "45621423", "20626359"]
airlines_names = ["KLM", "AirFrance", "British_Airways", "AmericanAir", "Lufthansa", "AirBerlin", "AirBerlin assist",
                  "easyJet", "RyanAir", "SingaporeAir", "Qantas", "EtihadAirways", "VirginAtlantic"]
airlines_other_id = ["56377143", "106062176", "18332190", "124476322", "26223583", "2182373406", "38676903",
                     "1542862735", "253340062", "218730857", "45621423", "20626359"]
airlines_other_names = ["KLM", "AirFrance", "British_Airways", "Lufthansa", "AirBerlin", "AirBerlin assist", "easyJet",
                        "RyanAir", "SingaporeAir", "Qantas", "EtihadAirways", "VirginAtlantic"]


class Conversation:
   
    tweets = {}
    reply_ids = []
   
    def __init__(self, tweets = {}):
        self.length = 0
        self.tweets_lst = []
        if tweets != {}:
            Conversation.tweets = tweets
 
    
    def setup(user_id, user_name):
        Conversation.user_id = user_id
        Conversation.user_name = user_name
    
 

    def addTweetDict(tweet_id, user, text, time, lang, reply_user = '', reply_tweet = ''):
        Conversation.tweets[tweet_id] = Tweet(tweet_id, user, text, time, lang, reply_user, reply_tweet)

    def addTweetConversation(self, tweet_id, end = False):
        tweet = Conversation.tweets[tweet_id]
        if end:
            self.tweets_lst.append(tweet_id)
        else:
            self.tweets_lst = [tweet_id] + self.tweets_lst
       
        tweet_id = tweet.reply_tweet
        if tweet.reply_tweet in Conversation.tweets.keys():
            self.addTweetConversation(tweet_id)
        elif tweet_id != None:
            if self.getTweet(tweet_id):
                self.addTweetConversation(tweet_id)
               
        self.length = len(self)

    def getTweet(self, tweetid):
       
        if tweetid in Conversation.tweets.keys():
            return Conversation.tweets[tweetid]
        else:
            q = """SELECT * FROM tweets WHERE tweet_id == {}""".format(tweetid)
            cursor = database.cursor()
           
            try:
                cursor.execute(q)
                tweet = cursor.fetchall()[0]
                database.commit()
                """id, date, user, text, replt tweet, reply user, lang"""
                Conversation.tweets[tweetid] = Tweet(tweet[0], tweet[2], tweet[3],
                                    tweet[1], tweet[6], tweet[4], tweet[5])
                return True
            except:
                database.commit()
                return None
   
   
    def addTweets(start_date = '2016-02-01 00:00:00', end_date = '2017-06-01 00:00:00'):

        query = """SELECT * FROM tweets WHERE (user_id == {} OR
            in_reply_to_user_id == {} OR text LIKE '%@{}%') AND
            datetime(created_at) >= datetime('{}') AND
            datetime(created_at) < datetime('{}');""".format(Conversation.user_id, 
            Conversation.user_id, Conversation.user_name, start_date, end_date)
        cursor = database.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        database.commit()
        for row in result:
            tweet_id = row[0]
            created = row[1]
            user = row[2]
            text = row[3]
            reply_tweet = row[4]
            reply_user = row[5]
            lang = row[6]
            Conversation.addTweetDict(tweet_id, user, text, created, lang,
                              reply_user, reply_tweet)

    def replyIdList():
        query = """SELECT in_reply_to_tweet_id FROM tweets
        WHERE in_reply_to_tweet_id NOT NULL;"""
        cursor = database.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        database.commit()
        Conversation.reply_ids = set([i[0] for i in result if i != 'None'])
        
    
    def containsUser(self):
        contains = False
        for tweet in self.tweets_lst:
            tweet = Conversation.tweets[tweet]
            if tweet.user == Conversation.user_id:
                contains = True
        return contains
   

    def __len__(self):
        if True:
            return len(self.tweets_lst)
        tweet = Conversation.tweets[self.tweets_lst[0]]
        if tweet.reply_tweet != '':
            return len(self.tweets_lst) + 1
        elif tweet.user in airlines_id and tweet.reply_user != None:
            return len(self.tweets_lst) + 1
        else:
            return len(self.tweets_lst)

    def __return__(self):
        return [Conversation.tweets[tweet] for tweet in self.tweets_lst]
       
 
class Tweet:
   
    def __init__(self, tweet_id, user, text, time, lang, reply_user = '', reply_tweet = ''):
        self.tweet_id = tweet_id
        self.user = user
        self.text = text
        self.lang = lang
        self.reply_user = reply_user
        self.reply_tweet = reply_tweet
        self.time = time
   
    def __str__(self):
        return 'ID:{} user:{} text:{} lang:{} reply_user:{} reply_tweet:{} created:{}'.format(self.tweet_id,
                   self.user, self.text, self.lang, self.reply_user, self.reply_tweet, self.time)
 
def listToDict(lst):
    dicti = {}
    for i in lst:
        if str(i) in dicti.keys():
            dicti[str(i)] = dicti[str(i)] + 1
        else:
            dicti[str(i)] = 1
    return dicti
 
def makeConversations(user_id, user_name):
    Conversation.setup(user_id, user_name)
    Conversation.replyIdList()
    Conversation.addTweets()

    for tweet_id in list(Conversation.tweets.keys()):
        if not tweet_id in Conversation.reply_ids:
            conversation = Conversation()
            conversation.addTweetConversation(tweet_id)
            if conversation.length > 1 and conversation.containsUser():
                conversationList.append(conversation)
    times = [len(conv) for conv in conversationList]
    return listToDict(times)


makeConversations(user_id = '22536055', user_name='AmericanAir')
times = [len(conv) for conv in conversationList]

dicti = listToDict(times)
print(dicti)


 
def processTweet(tweet):
    # process the tweets
 
    #Convert to lower case
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www.[^\s]+)|(https?://[^\s]+))','URL',tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    return tweet

tweet_ids_lst = []
tweet_text_lst = []
tweet_sentiment_score = []
counter = 0
for key in Conversation.tweets.keys():
    tweet_ids_lst.append(key)
    
    proctweet = processTweet(Conversation.tweets[key].text)
    tweet_text_lst.append(proctweet)
    
    blob = TextBlob(proctweet)
    tweet_sentiment_score.append(blob.sentiment.polarity)
    print(counter)
    counter += 1


for i in range(len(tweet_ids_lst)):
    conversation.tweets[tweet_ids_lst[i]].sentiment = tweet_sentiment_score[i]


