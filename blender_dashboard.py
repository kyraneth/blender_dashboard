import streamlit as st
import tweepy
import pandas as pd
import datetime

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

st.set_page_config(layout="wide")
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

  df.to_csv('tweet_ranking.csv', index=False)

  # Update the search date file
  with open('search_date.txt', 'w') as f:
    f.write(datetime.datetime.now().strftime("%A %d %B %Y, %H:%M"))

# Read the search date from the file
try:
  with open('search_date.txt', 'r') as f:
    search_date = f.read()
except:
  search_date = 'No previous search'

# Display the search date
st.markdown(f'Last search: {search_date}')

# Get the current date and time
current_datetime = datetime.datetime.now()

# Get the color for the generate data button based on the time difference between the current date and the search date
button_color = '#00e676'  # green
try:
  search_datetime = datetime.datetime.strptime(search_date, "%A %d %B %Y, %H:%M")
  time_difference = current_datetime - search_datetime
  if time_difference.total_seconds() > 3600:  # more than 1 hour
    button_color = '#ff1744'  # red
except:
  pass

if st.button('Generate data', button_color=button_color):
  search_and_rank_tweets()

# Load the top tweets from the CSV file
df = pd.read_csv('tweet_ranking.csv')

try:
    # Get the number of tweets to show from the slider
    n = st.slider('Number of tweets to show', 10, 100)

    # Add a checkbox to filter the dataframe to only show entries with engagement scores >= 1
    filter_engagement = st.checkbox('Filter by engagement score')
    if filter_engagement:
        f = st.slider('filter engagement higher than:', 0, 10)
        df = df[df['engagement_score'] >= f]

    # Display the top tweets
    st.dataframe(df[['URL', 'engagement_score', 'like_count', 'reply_count', 'retweet_count', 'quote_count']][:n],
                 width=1000, height=300)
    st.markdown(f'Showing top {len(df)} tweets')

except Exception as e:
  st.write("Please Generate Data")
  st.write(e)