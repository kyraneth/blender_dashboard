import streamlit as st
import tweepy
import pandas as pd
import datetime
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
tab1, tab2 = st.tabs(["Twitter", "Reddit"])
# Enter your API keys and secrets here
consumer_key = 'jIOfcFvFLUSPaQ4CoYtLuEA5E'
consumer_secret = '1HBuH1xJPyWW1580NEkrKTkuR83tjqgU0kgvKmWth0sdFCdyiG'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAACmYkwEAAAAAP%2B7dibHCwGglWM0FPlJf2fdUM6c%3DYmAGe'

# Set up the Client object
client = tweepy.Client(
  'AAAAAAAAAAAAAAAAAAAAACmYkwEAAAAAeYuTpKMtaqZCivRpHOIOgaPGbY8%3DcDXBUQBk0VCc1OWrh7ZOiAsvvKueJtUHc5jezouPcPxcQ0XhvI'
)

# Set the search term and time span
query = '(Geometry Nodes OR geonodes OR geometrynodes) -is:retweet'

st.title('Geometry Nodes over the Last 7 Days')

def search_and_rank_tweets():
  # Search for tweets
  tweets = tweepy.Paginator(client.search_recent_tweets, query=query,
                                       tweet_fields=['public_metrics','author_id','text','created_at'],
                                       expansions=['entities.mentions.username','author_id'],
                                       user_fields=['username'],
                                       max_results=100).flatten(limit=100000)

  tweet_data = []
  for tweet in tweets:
    tweet_data.append({
      'URL': f"https://twitter.com/twitter/status/{tweet.id}",
      'tweet_author' : tweet['author_id'],
      'tweet_text' : tweet['text'],
      'created_at' : tweet['created_at'],
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

  # Save the search date to a file
  search_date = datetime.datetime.now().strftime("%A %d %B %Y, %H:%M")
  with open('search_date.txt', 'w') as f:
    f.write(search_date)

  df.to_csv('tweet_ranking.csv', index=False)

  return df

# Read the search date from the file
try:
  with open('search_date.txt', 'r') as f:
    search_date = f.read()
except:
  search_date = "No data generated yet"

with tab1:
  if st.button('Generate data'):

    # Display the top tweets
    search_and_rank_tweets()

  # Display the search date and a warning message if the data is more than 1 hour old
  if "No data generated yet" in search_date:
    st.write(search_date)
  else:
    current_date = datetime.datetime.now()
    search_date = datetime.datetime.strptime(search_date, "%A %d %B %Y, %H:%M")
    time_difference = current_date - search_date
    if time_difference.total_seconds() / 3600 > 1:
      st.write("Data might be out of date, generate data")
    else:
      st.write("Data less than 1 hour old")

  df = pd.read_csv('tweet_ranking.csv')

  try:
      n = st.slider('Number of tweets to show', 10, 100)
      filter_engagement = st.checkbox('Filter by engagement score')
      if filter_engagement:
          f = st.slider('filter engagement higher than:', 0, 10)
          df = df[df['engagement_score'] >= f]  
      st.dataframe(df[['URL', 'engagement_score', 'like_count', 'reply_count', 'retweet_count', 'quote_count', 'created_at', 'tweet_text', 'tweet_author']][:n],
                  width=1000, height=300)
      st.markdown(f'Showing top {len(df[:n])} tweets')

  except:
      st.write("Please Generate Data")
