import tweepy
from textblob import TextBlob
import json
import csv

consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
access_token = "YOUR_ACCESS_TOKEN"
access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def perform_sentiment_analysis(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    return polarity

def process_tweets(query, limit):
    tweets = tweepy.Cursor(api.search, q=query).items(limit)

    with open('tweets.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Tweet", "Sentiment"])

        for tweet in tweets:
            processed_tweet = tweet.text.encode('utf-8')

            sentiment = perform_sentiment_analysis(processed_tweet)
            
            writer.writerow([processed_tweet.decode('utf-8'), sentiment])

query = "#example"
limit = 100

process_tweets(query, limit)
