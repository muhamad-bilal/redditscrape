
import praw
from time import sleep
import praw.exceptions
import pandas as pd
from datetime import datetime

# Replace with your Reddit app credentials
client_id = "glP5AXIGG1cBmIlGfzRE7g"
client_secret = "HzPL3z5BHdgAZE1U8V926ewj9ozAZg"
user_agent = "PaleontologistSea714 "
# Initialize Reddit client
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

# Function to collect posts (no cleaning this time)
def collect_reddit_posts(subreddit, celebrity, limit=10, delay=1):
    posts_data = []
    for submission in subreddit.search(query=celebrity, limit=limit):
        try:
            post_info = {
                'Post ID': submission.id,
                'Post Author': submission.author.name if submission.author else "[deleted]",
                'Post Title': submission.title,
                'Post Content': submission.selftext,
                'Post Time': datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                'Subreddit': submission.subreddit.display_name  # Always include subreddit
            }
            posts_data.append(post_info)
            sleep(delay)
        except praw.exceptions.APIException as e:
            print(f"API Error: {e}")
            break
    return posts_data

# Hardcoded subreddit and celebrity
celebrity = "asus"
subreddit = reddit.subreddit("ASUS")  # Search all of Reddit

# Collecting posts with rate limiting
posts_data = collect_reddit_posts(subreddit, celebrity)

# Create DataFrame and save to Excel
df = pd.DataFrame(posts_data)
df.to_excel("sui.xlsx", index=False)
