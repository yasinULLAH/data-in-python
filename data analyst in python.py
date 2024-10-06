# Import Libraries
import tweepy
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from datetime import datetime

# Twitter API Credentials
API_KEY = 'YOUR_API_KEY'
API_SECRET = 'YOUR_API_SECRET'
ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
ACCESS_SECRET = 'YOUR_ACCESS_SECRET'

# Authenticate to Twitter
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Define Categories and Keywords
categories = {
    'fitness': ['#fitness', 'fitness', 'workout', 'gym', 'health'],
    'tech': ['#tech', 'technology', 'gadgets', 'innovation', 'AI'],
    'family': ['#family', 'family', 'parenting', 'kids', 'home'],
    'food': ['#food', 'foodie', 'cooking', 'recipes', 'restaurant']
}

# Collect Tweets
def collect_tweets(category, keywords, max_tweets=100):
    query = ' OR '.join(keywords) + ' -filter:retweets'
    tweets = tweepy.Cursor(api.search_tweets, q=query, lang='en', tweet_mode='extended').items(max_tweets)
    data = []
    for tweet in tweets:
        data.append({
            'category': category,
            'created_at': tweet.created_at,
            'text': tweet.full_text,
            'retweet_count': tweet.retweet_count,
            'favorite_count': tweet.favorite_count,
            'user_followers': tweet.user.followers_count
        })
    return data

all_tweets = []
for category, keywords in categories.items():
    all_tweets.extend(collect_tweets(category, keywords))

df = pd.DataFrame(all_tweets)

# Data Cleaning
def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    return text

df['clean_text'] = df['text'].apply(clean_text)

# Sentiment Analysis
def get_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

df['sentiment'] = df['clean_text'].apply(get_sentiment)

# Analysis
engagement = df.groupby('category').agg({
    'retweet_count': 'mean',
    'favorite_count': 'mean',
    'user_followers': 'mean',
    'sentiment': 'mean',
    'text': 'count'
}).rename(columns={'text': 'tweet_count'}).reset_index()

# Visualization
sns.set(style="whitegrid")

# Average Retweets and Favorites
plt.figure(figsize=(10,6))
sns.barplot(x='category', y='retweet_count', data=engagement, palette='Blues_d')
plt.title('Average Retweets per Category')
plt.xlabel('Category')
plt.ylabel('Average Retweets')
plt.show()

plt.figure(figsize=(10,6))
sns.barplot(x='category', y='favorite_count', data=engagement, palette='Greens_d')
plt.title('Average Favorites per Category')
plt.xlabel('Category')
plt.ylabel('Average Favorites')
plt.show()

# Average Sentiment
plt.figure(figsize=(10,6))
sns.barplot(x='category', y='sentiment', data=engagement, palette='Oranges_d')
plt.title('Average Sentiment per Category')
plt.xlabel('Category')
plt.ylabel('Average Sentiment')
plt.show()

# Tweet Count
plt.figure(figsize=(10,6))
sns.barplot(x='category', y='tweet_count', data=engagement, palette='Purples_d')
plt.title('Number of Tweets per Category')
plt.xlabel('Category')
plt.ylabel('Tweet Count')
plt.show()

# Save Analysis
engagement.to_csv('social_media_analysis.csv', index=False)
