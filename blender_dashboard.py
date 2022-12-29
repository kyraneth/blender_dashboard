import streamlit as st
import tweepy
import pandas as pd
import streamlit.components.v1 as components

# Enter your API keys and secrets here
consumer_key = 'jIOfcFvFLUSPaQ4CoYtLuEA5E'
consumer_secret = '1HBuH1xJPyWW1580NEkrKTkuR83tjqgU0kgvKmWth0sdFCdyiG'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAACmYkwEAAAAAP%2B7dibHCwGglWM0FPlJf2fdUM6c%3DYmAGe'

# Set up the Client object
client = tweepy.Client(
  'AAAAAAAAAAAAAAAAAAAAACmYkwEAAAAAeYuTpKMtaqZCivRpHOIOgaPGbY8%3DcDXBUQBk0VCc1OWrh7ZOiAsvvKueJtUHc5jezouPcPxcQ0XhvI'
)

# Set the search term and time span
query = '(Geometry Nodes OR geonodes OR geometry nodes) -is:retweet'

st.title('Geometry Nodes over the Last 7 Days')

def search_and_rank_tweets():
  # Search for tweets
  tweets = tweepy.Paginator(client.search_recent_tweets, query=query,
                                       tweet_fields=['public_metrics'],
                                       max_results=100).flatten(limit=100000)

  tweet_data = []
  for tweet in tweets:
    tweet_data.append({
      'URL': f"https://twitter.com/twitter/status/{tweet.id}",
      'retweet_count': tweet['public_metrics']['retweet_count'],
      'reply_count': tweet['public_metrics']['reply_count'],
      'like_count': tweet['public_metrics']['like_count'],
      'quote_count': tweet['public_metrics']['quote_count']
    })

  df = pd.DataFrame(tweet_data)

  # Calculate the engagement score using the specified weights
  df['engagement_score'] = (df['like_count'] * 0.15 +
                             df['retweet_count'] * 0.20 +
                             df['quote_count'] * 0.25 + 
                             df['reply_count'] * 0.40)

  # Sort the DataFrame by engagement score in descending order
  df.sort_values(by='engagement_score', ascending=False, inplace=True)

  return df


if st.button('Generate data'):

  # Display the top tweets
  df = search_and_rank_tweets()
  


try:
    n = st.slider('Number of tweets to show', 10, 100)
    st.dataframe(df[['URL', 'engagement_score', 'like_count', 'reply_count', 'retweet_count', 'quote_count']],
                width=700, height=300)
    st.markdown(f'Showing top {n} tweets')
except:
    st.write("Please Generate Data")

if st.button('Refresh Range'):
    st.dataframe(df[['URL', 'engagement_score', 'like_count', 'reply_count', 'retweet_count', 'quote_count']],
                width=700, height=300)
    st.markdown(f'Showing top {n} tweets')


st.write("Reddit Feed")
components.iframe("https://www.reddit.com/r/blender")