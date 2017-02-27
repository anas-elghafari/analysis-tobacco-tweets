'''
Script originally written by Kunal Relia.  
This version has been modified by Anas Elghafari
Changes include:
    checking rate_limit and using that to calculate number of calls per keyword
    not using Cursor object (as it can make an arbitrary number of calls to the API)
 
'''


from collections import OrderedDict
from datetime import date
import tweepy, time, json, csv
#import MySQLdb as mdb
import sys

#con = mdb.connect('localhost', 'root', '', 'temp',use_unicode=True, charset="utf8")
    
#cur = con.cursor() 

with open('config.json') as data_file:
    jsondt = json.load(data_file)

  
auth = tweepy.auth.OAuthHandler(jsondt['consumer_key'], jsondt['consumer_secret'])
auth.set_access_token(jsondt['access_token_key'], jsondt['access_token_secret'])
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

outfile_object = open('TrainingSetTobaccoTweets.csv','a',encoding='utf-8')
outfile = csv.writer(outfile_object,delimiter=',',lineterminator='\n')
outfile.writerow(['created_at', 'class', 'user_screen_name', 'tweet', 'tweet_id', 'retweet count', 'coordinates'])

def writeTweetsToCsv(tweet,query,class_of_tob):
        outfile.writerow([tweet['created_at'], class_of_tob, tweet['user']['screen_name'],
                          tweet['text'],tweet['id'],tweet['retweet_count'],tweet['coordinates']])

def writeTweetsToDb(tweets,query,con,cur,class_of_tob):
    # Write name of selected user
    try:
        lat=tweets.coordinates['coordinates'][0]
        long=tweets.coordinates['coordinates'][1]
        #print 'yes'
    except:
        lat="None"
        long="None"
        #print 'no'

    
    try:
        # cur.execute("""INSERT INTO tweets (`Date`, `Favorites`,`ID`, `Language`, `Retweeted`, `Source`, `Text`, `Truncated`, `Description`, `Favourite Count`, `Followers Count`, `Friends Count`, `Listed Count`, `Location`, `Name`, `Protected`, `Screen Name`, `user_id`, `user_created_at`, `user_utc_offset`, `lat`, `long`, `Statuses Count`, `Application` ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(tweets.created_at,tweets.favorited,tweets.id,tweets.lang,tweets.retweeted,tweets.source,(tweets.text).encode('utf8'),tweets.truncated,tweets.user.description.encode('utf8'),tweets.user.favourites_count,tweets.user.followers_count, tweets.user.friends_count,tweets.user.listed_count,(tweets.user.location).encode('utf8'),(tweets.user.name).encode('utf8'),tweets.user.protected, tweets.user.screen_name, tweets.user.id_str, tweets.user.created_at, tweets.user.utc_offset, lat, long, tweets.user.statuses_count,query ))
        # cur.execute("INSERT INTO tweets (`Date` ) VALUES (%s)",(tweets.text))
        # cur.execute("INSERT INTO birthday_tweets (`bt_id`, `user_id`, `age`, `tweet_id`, `tweet`) VALUES (NULL,%d,%d,%d,%s)", (tweets.user['id'],age_ctr,tweets.id_str,tweets.text))
        # con.commit()
        cur.execute("INSERT INTO tobacco_detailed_with_tweets (`day_id`, `day`, `category`, `user_id`, `tweet`) VALUES (NULL,%s,%s,%s,%s)",(tweets.created_at.weekday(), class_of_tob,tweets.user.id,tweets.text))
        con.commit()

    except mdb.Error as err:  
        print(err)
        
        con.rollback()

file_object = open("tobacco_keywords_one.csv")    
csv_reader = csv.reader(file_object)
csv_reader.__next__() #skipping over the header
keyword_to_class = OrderedDict()
for row in csv_reader:
    keyword_to_class[row[0]] = row[1]


num_tweets_requested=100 #the maximum that twitter API returns anyway
search_calls_available = api.rate_limit_status()['resources']['search']['/search/tweets']['remaining']
search_calls_per_keyword = int((search_calls_available - 5) / len(keyword_to_class.keys()))
print("API Search calls remaining: ", search_calls_available, " -- calls per keyword: ", search_calls_per_keyword, "\n\n")


for keyword, tob_class in keyword_to_class.items():
    #wait_time_seconds = 10
    new_tweets = []
    try:
        print ("\n\nSearch term now: ", keyword, " ----- class of the keyword: ", str(tob_class))
        for i in range(search_calls_per_keyword):
            results = api.search(
                           q=keyword,
                           count=num_tweets_requested,
                           result_type="recent",
                           include_entities=False,
                           lang="en")
            new_tweets.extend([results['statuses'][i] for i in range(len(results['statuses']))])
        print('downloaded...')
        print("number of new_tweets: ", len(new_tweets))
        if not new_tweets:
            print('No search results found')
        else:
            newtweets_count = 0
            rttweets_count = 0
            for tweet in new_tweets:
              if "RT " not in tweet['text']:
                  #writeTweetsToDb(tweet,query,con,cur,class_of_tobacco[i])
                  writeTweetsToCsv(tweet,keyword,tob_class)
                  newtweets_count += 1
              else:
                  rttweets_count +=1              

        print("Number of new tweets found and written to file: " + str(newtweets_count))
        print("Number of rt tweets found and discarded: " + str(rttweets_count))


    except tweepy.TweepError as e:
        # depending on TweepError.code, one may want to retry or wait
        # to keep things simple, we will give up on an error
        print(e)
        print('bad twitter! bad!')

    #print('Will wait {0} sec to avoid rate-limit'.format(wait_time_seconds))
    #time.sleep(wait_time_seconds)

outfile_object.close()
file_object.close()
#cur.close()
#con.close()

