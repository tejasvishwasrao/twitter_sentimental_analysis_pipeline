#from lib2to3.pgen2.pgen import DFAState
from fileinput import filename
import pickle
import numpy as np
import tweepy
import configparser
import pandas as pd
import re
import string
from textblob import TextBlob 

# NLP preprocessing libraries
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# read configs
config = configparser.ConfigParser()
config.read('config.ini')


api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']

access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']


# authentication
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

public_tweets = api.home_timeline()


df = pd.DataFrame(columns=["target","t_id", "created_at", "user", "text"])
#print(df)


def get_tweets(topic, count):
    i = 0
    for tweet in tweepy.Cursor(api.search_tweets, q=topic, count=100, lang="en").items():
        #print(i, end='\r')
        df.loc[i, "t_id"] = tweet.id
        df.loc[i, "created_at"] = tweet.created_at
        #df.loc[i, "query"] = tweet.query
        df.loc[i, "user"] = tweet.user.name
        #df.loc[i, "IsVerified"] = tweet.user.verified
        df.loc[i, "text"] = tweet.text
        #df.loc[i, "Likes"] = tweet.favorite_count
        #df.loc[i, "RT"] = tweet.retweet_count
        #df.loc[i, "User_location"] = tweet.user.location
        df.to_csv('TweetDataset.csv')
        i = i + 1
        if i > count:
            break
        else:
            pass


# Call the function to extract the data. pass the topic and filename you want the data to be stored in.
Topic = ["Ukraine"]

get_tweets(Topic, count=100)

#print(df.head(8))

# Global Parameters
stop_words = set(stopwords.words('english'))

def remove_unwanted_cols(df, cols):
    for col in cols:
        del df[col]
    return df

# We only want the Text so :

# (@[A-Za-z0-9]+)   : Delete Anything like @hello @Letsupgrade etc
# ([^0-9A-Za-z \t]) : Delete everything other than text,number,space,tabspace
# (\w+:\/\/\S+)     : Delete https://
# ([RT]) : Remove "RT" from the tweet

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
    vector = TfidfVectorizer(max_features=50)
    vector.fit(train_fit)
    return vector

# Analyze the tweets
def analyze_sentiment(tweet):
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        return 'Positive'
    elif analysis.sentiment.polarity == 0:
        return 'Neutral'
    else:
        return 'Negative'

# Remove unwanted columns from dataset
df = remove_unwanted_cols(df, ['t_id', 'created_at', 'user'])

#df["target"] = np.nan

#df = df[['target', 'text']]

#Preprocess data
df.text = df['text'].apply(preprocess_tweet_text)

print(df) 

print(df.columns)

tf_vector = get_feature_vector(np.array(df.iloc[:, 1]).ravel())
X = tf_vector.transform(np.array(df.iloc[:, 1]).ravel())

# load the model from disk
with open('model.pkl' , 'rb') as f:   
    lr = pickle.load(f)
df['target'] = lr.predict(X)

print(df.head(5))
 
#df["Sentiment"] = df["Tweet"].apply(lambda x: analyze_sentiment(x))

#print(df.head(5))
print('length of data is', len(df))


##import packages
from flask import render_template, Flask

##create an instance of flask class for our app.
app = Flask(__name__)

#creates url
@app.route('/')

##Function to create first welcome page of TT.
def table():
    return df.to_html()

##run the application on local deployment server.
if __name__ == "__main__":
    app.run(host='0.0.0.0')
