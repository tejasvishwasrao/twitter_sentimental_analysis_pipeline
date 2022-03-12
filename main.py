from matplotlib.pyplot import text
import pandas as pd
import numpy as np
import re
import string
import sys

# NLP preprocessing libraries
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

# ML Libraries
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

# MLFlow libraries
from urllib.parse import urlparse
import mlflow
import mlflow.sklearn
# Logger library
import logging
import configparser
import pandas as pd
import re
from textblob import TextBlob

import tweepy
import configparser
import pandas as pd
import re
from textblob import TextBlob

# Global Parameters
stop_words = set(stopwords.words('english'))

def load_dataset(filename, cols):
    dataset = pd.read_csv(filename, encoding='latin-1')
    dataset.columns = cols
    return dataset

def remove_unwanted_cols(dataset, cols):
    for col in cols:
        del dataset[col]
    return dataset

def preprocess_tweet_text(tweet):
    tweet.lower()
    # Remove urls
    tweet = re.sub(r"http\S+|www\S+|https\S+", '', tweet, flags=re.MULTILINE)
    # Remove user @ references and '#' from tweet
    tweet = re.sub(r'\@\w+|\#','', tweet)
    # Remove punctuations
    tweet = tweet.translate(str.maketrans('', '', string.punctuation))
    # Remove stopwords
    tweet_tokens = word_tokenize(tweet)
    filtered_words = [w for w in tweet_tokens if not w in stop_words]
    
    #ps = PorterStemmer()
    #stemmed_words = [ps.stem(w) for w in filtered_words]
    #lemmatizer = WordNetLemmatizer()
    #lemma_words = [lemmatizer.lemmatize(w, pos='a') for w in stemmed_words]
    
    return " ".join(filtered_words)

def get_feature_vector(train_fit):
    vector = TfidfVectorizer(sublinear_tf=True)
    vector.fit(train_fit)
    return vector


def int_to_string(sentiment):
    if sentiment == 0:
        return "Negative"
    elif sentiment == 2:
        return "Neutral"
    else:
        return "Positive"


# read configs
config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']

access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

# authentication
auth = tweepy.OAuth1UserHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# public_tweets = api.home_timeline()

# create dataframe
# To get the tweets in a Proper format, first lets create a Dataframe to store the extracted data.

t_dataset = pd.DataFrame(columns=["t_id", "created_at", "user", "text",])
print(t_dataset)

def get_tweets(topic, count):
    i = 0
    for tweet in tweepy.Cursor(api.search_tweets, q=topic, count=100, lang="en").items():
        print(i, end='\r')
        t_dataset.loc[i, "t_id"] = tweet.id
        t_dataset.loc[i, "created_at"] = tweet.created_at
        t_dataset.loc[i, "user"] = tweet.user
        t_dataset.loc[i, "text"] = tweet.text
        t_dataset.to_csv('TweetDataset.csv', index=False)
        i = i + 1
        if i > count:
            break
        else:
            pass


# Call the function to extract the data. pass the topic and filename you want the data to be stored in.
Topic = ["Arsenal"]

get_tweets(Topic, count=100)


t_dataset = remove_unwanted_cols(t_dataset, ['t_id', 'created_at','user'])

#Preprocess data
t_dataset.text = t_dataset['text'].apply(preprocess_tweet_text)

print(t_dataset.head())

##import packages
from flask import render_template, Flask

##create an instance of flask class for our app.
app = Flask(__name__)

#creates url
@app.route('/')

##Function to create first welcome page of TT.
def index():
    return "Welcome"

##run the application on local deployment server.
if __name__ == "__main__":
    app.run(host='0.0.0.0')
