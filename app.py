from flask import Flask,request,jsonify
import pandas as pd
import tweepy as tw
import json
import numpy as np
import requests

#############################################################################################
################################  TWEEPY SETUP  #############################################

consumer_key = 'KNY4Zvfpg3ZJw9HEXgYZgpEsV'
consumer_secret = 'omlOAjdQViBKm1IKVWQfa0xuPakw6qs8G3YgnVM796KuaEabVz'
access_token = '60773330-kwmBd0SRPws1b0xl9EqF6hqOGuzXp0gxU9dX1HKZi'
access_token_secret = 'Lxl9jZJIcS2QresKsaRaSEcxcCly5JVuA6gVBtrveY9Eh'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth)

# #############################################################################################
# ################################  SENTIMENT SETUP  ##########################################
url = "https://api.aiforthai.in.th/ssense"

headers = {
    'Apikey': "NAgeMIZvAm7KiAfBrLnHPrXWrITGA8aq"
    }

# #############################################################################################

app = Flask(__name__)

def search_tweets():
    
    # Define the search term and the date_since date as variables
    search_words = request.args.get("keyword")

    new_search = search_words + "-filter:retweets" # Do not get retweet of tweets
    
    #collect tweets
    tweets = tw.Cursor(api.search_tweets, q = new_search,  lang = 'th' ).items(10)
    
    users_locs = [[ tweet.created_at, tweet.text, tweet.user.followers_count,tweet.retweet_count, tweet.favorite_count] for tweet in tweets]
    
    # To dateframe
    tweet_df = pd.DataFrame(data=users_locs, columns=['time_stamp', 'text', 'followers_count', 'retweet_count','favorite_count'])

    # To Json  
    result = tweet_df['text'].to_json(orient="records")
    parsed = json.loads(result)

    return parsed


def test_sentiments(text):
    params = {'text':text}
    response = requests.get(url, headers=headers, params=params)
    datajson = response.json()
    keyword = datajson["preprocess"]['input']
    sentiment = datajson["sentiment"]['polarity']
    score = datajson["sentiment"]['score']
    result = np.array([keyword , sentiment, score])
    return result

# #############################################################################################

def sentiment_analyst():
    test = []
    for i in search_tweets():
        test.append(test_sentiments(i))
    df = pd.DataFrame(test, columns = ['text','sentiment','score',])
    result = df.to_json(orient="records")
    parsed = json.loads(result)
    return jsonify(parsed)


@app.route('/', methods=['GET'])
def home():
    return 'Hello World'

@app.route('/api/twitter-sentiments', methods=['GET'])
def get_api():
    return sentiment_analyst()

if __name__ == "__main__":
    app.run(debug=True)

    