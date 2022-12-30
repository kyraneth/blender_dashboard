import streamlit as st
import tweepy
import pandas as pd
import datetime
import streamlit.components.v1 as components
import praw

### TWITTER SEARCH FUNCTION #####

st.set_page_config(layout="wide")


def search_and_rank_tweets():

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
  search_date_twitter = datetime.datetime.now().strftime("%A %d %B %Y, %H:%M")
  with open('search_date_twitter.txt', 'w') as f:
    f.write(search_date_twitter)

  df.to_csv('tweet_ranking.csv', index=False)

  return df



###REDDIT SEARCH FUNCITON###
def search_rank_reddit():
  # Set up the Reddit API client
  reddit = praw.Reddit(client_id='URIqIadG09bOsdLi67eA1Q',
                      client_secret='BZM_d0w6SkTQDV2BYWUCL1cA-bWr-Q',
                      user_agent='Blender_Data_Check')

  # Set up an empty list to store the data we retrieve
  data_reddit = []

  # Set the search term and subreddit to search in
  search_term = 'geometry nodes OR geonodes OR geometry nodes'
  subreddit = 'blender'

  # Search for the given term in the subreddit
  for submission in reddit.subreddit(subreddit).search(search_term, time_filter='week'):
      # For each submission, store the relevant data in a dictionary
      submission_data = {
          'user': submission.author,
          'upvotes': submission.score,
          'comments': submission.num_comments,
          'title': submission.title,
          'content': submission.selftext,
          'URL': submission.url,
          'engagement_score': (submission.score + submission.num_comments) / 2
      }
      # Add the dictionary to the list
      data_reddit.append(submission_data)

  # Convert the list of dictionaries to a Pandas dataframe
  df_reddit = pd.DataFrame(data_reddit)

  # Sort the dataframe by the "engagement_score" column in descending order
  df_reddit = df_reddit.sort_values(by='engagement_score', ascending=False)

  search_date_reddit = datetime.datetime.now().strftime("%A %d %B %Y, %H:%M")
  with open('search_date_reddit.txt', 'w') as f:
    f.write(search_date_reddit)

  df_reddit.to_csv('reddit_ranking.csv', index=False)

  # Display the dataframe
  print(df_reddit)

''''''''''''''''''
'''''''''''''''


GENERAL SECTION


'''''''''''''''
''''''''''''''''''



st.title('Geometry Nodes over the Last 7 Days')
tab1, tab2 = st.tabs(["Twitter", "Reddit"])



#TWITTER SECTION




# Read the search date from the file
try:
  with open('search_date_twitter.txt', 'r') as f:
    search_date_twitter = f.read()
except:
  search_date_twitter = "No data generated yet"

with tab1:

  
  header=st.container()
  with header:
    col1, col2, col3 = st.columns(3)
  with header:
    with col1:
      if st.button('Generate Twitter data'):

        # Display the top tweets
        search_and_rank_tweets()

  # Display the search date and a warning message if the data is more than 1 hour old
  table = st.container()
  if "No data generated yet" in search_date_twitter:
    st.write(search_date_twitter)
  else:
    current_date = datetime.datetime.now()
    search_date = datetime.datetime.strptime(search_date_twitter, "%A %d %B %Y, %H:%M")
    time_difference = current_date - search_date

    with header:
      with col2:
        if time_difference.total_seconds() / 3600 > 1:
          st.write(":red[Data might be out of date, generate data]")
        else:
          st.write(":green[Data less than 1 hour old]")

  df = pd.read_csv('tweet_ranking.csv')

  try:
      n = st.slider('Number of tweets to show', 10, 100)
      filter_engagement = st.checkbox('Filter by engagement score')
      if filter_engagement:
          f = st.slider('filter engagement higher than:', 0, 10)
          df = df[df['engagement_score'] >= f]  
      with table:
        st.dataframe(df[['URL', 'engagement_score', 'like_count', 'reply_count', 'retweet_count', 'quote_count', 'created_at', 'tweet_text', 'tweet_author']][:n],
                     width=1000, height=300)
      with header:
        with col3:
          st.markdown(f'Showing top {len(df[:n])} tweets')

  except:
      st.write("Please Generate Data")




###REDDIT SECTION



try:
  with open('search_date_reddit.txt', 'r') as f:
    search_date_reddit = f.read()
except:
  search_date_reddit = "No data generated yet"

with tab2:

  
  header_2=st.container()
  with header_2:
    col1_2, col2_2, col3_2 = st.columns(3)
  with header_2:
    with col1_2:
      if st.button('Generate Reddit data'):

        # Display the top tweets
        search_rank_reddit()

  # Display the search date and a warning message if the data is more than 1 hour old
  table_2 = st.container()
  if "No data generated yet" in search_date_reddit:
    st.write(search_date_reddit)
  else:
    current_date_2 = datetime.datetime.now()
    search_date_2 = datetime.datetime.strptime(search_date_reddit, "%A %d %B %Y, %H:%M")
    time_difference_2 = current_date_2 - search_date_2

    with header_2:
      with col2_2:
        if time_difference_2.total_seconds() / 3600 > 1:
          st.write(":red[Data might be out of date, generate data]")
        else:
          st.write(":green[Data less than 1 hour old]")

  df_2 = pd.read_csv('reddit_ranking.csv')

  try:
      n_2 = st.slider('Number of reddit posts to show', 10, 100)
      filter_engagement_2 = st.checkbox('Filter by engagement score')
      if filter_engagement_2:
          f_2 = st.slider('filter engagement higher than:', 0, 10)
          df_2 = df[df['engagement_score'] >= f_2]  
      with table_2:
        st.dataframe(df[['url', 'engagement_score', 'title', 'upvotes', 'comments', 'user', 'content']][:n],
                     width=1000, height=300)
      with header_2:
        with col3_2:
          st.markdown(f'Showing top {len(df[:n])} tweets')

  except:
      st.write("Please Generate Data")