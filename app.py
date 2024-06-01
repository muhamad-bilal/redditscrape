import praw
from time import sleep
import praw.exceptions
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory
import os
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

# Your Reddit credentials (move these to environment variables for security)
client_id = "glP5AXIGG1cBmIlGfzRE7g"
client_secret = "HzPL3z5BHdgAZE1U8V926ewj9ozAZg"
user_agent = "PaleontologistSea714 "

reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)


def collect_reddit_posts(subreddit, celebrity, limit, delay=1):
    posts_data = []
    for submission in subreddit.search(query=celebrity, limit=limit):
        try:
            post_content = submission.selftext

            # Use regular expression to remove image URLs
            post_content = re.sub(r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', '', post_content)

            post_info = {
                'Post ID': submission.id,
                'Post Author': submission.author.name if submission.author else "[deleted]",
                'Post Title': submission.title,
                'Post Content': post_content,  # Store the cleaned content
                'Post Time': datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                'Subreddit': submission.subreddit.display_name
            }
            posts_data.append(post_info)
            sleep(delay)
        except praw.exceptions.APIException as e:
            print(f"API Error: {e}")
            break
    return posts_data


@app.route('/', methods=['GET', 'POST'])
def index():
    excel_filename = None
    if request.method == 'POST':
        celebrity = request.form['celebrity']
        subreddit_name = request.form['subreddit']
        limit = int(request.form['limit'])  # Get limit from form

        try:
            subreddit = reddit.subreddit(subreddit_name)
            posts_data = collect_reddit_posts(subreddit, celebrity,limit)
            
            if posts_data:  # Only create and save Excel if there are posts
                df = pd.DataFrame(posts_data)
                excel_filename = f"reddit_posts_{celebrity}_{subreddit_name}.xlsx"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], excel_filename)
                df.to_excel(filepath, index=False)

            return render_template('result.html', 
                                   posts=posts_data, 
                                   celebrity=celebrity, 
                                   subreddit=subreddit_name,
                                   excel_filename=excel_filename)  
        except praw.exceptions.RedditAPIException as e:
            error_message = f"Error accessing subreddit: {e}"
            return render_template('index.html', error=error_message)
    # Ensure excel_filename is passed to the template even if it's None
    return render_template('index.html', excel_filename=excel_filename) 

@app.route('/download/<filename>') 
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True) 
