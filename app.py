import streamlit as st
import os
import csv
from Senti import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment
from YoutubeCommentScrapper import save_video_comments_to_csv, get_channel_info, youtube, get_channel_id, get_video_stats
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))

st.set_page_config(page_title='Sentimental Analysis', page_icon='LOGO.png', initial_sidebar_state='auto')
st.sidebar.title("Sentimental Analysis")
st.sidebar.header("Enter YouTube Link")
youtube_link = st.sidebar.text_input("Link")
directory_path = os.getcwd()
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

if youtube_link:
    video_id = extract_video_id(youtube_link)
    channel_id = get_channel_id(video_id)
    if video_id:
        st.sidebar.write("The video ID is:", video_id)
        csv_file = save_video_comments_to_csv(video_id)
        delete_non_matching_csv_files(directory_path, video_id)
        st.sidebar.write("Comments saved to CSV!")
        st.sidebar.download_button(label="Download Comments", data=open(csv_file, 'rb').read(), file_name=os.path.basename(csv_file), mime="text/csv")

        channel_info = get_channel_info(youtube, channel_id)

        col1, col2 = st.columns(2)

        with col1:
            channel_logo_url = channel_info['channel_logo_url']
            st.image(channel_logo_url, width=250)

        with col2:
            channel_title = channel_info['channel_title']
            st.title(' ')
            st.text("  YouTube Channel Name  ")
            st.title(channel_title)
            st.title("  ")
            st.title(" ")
            st.title(" ")

        st.title(" ")
        col3, col4, col5 = st.columns(3)

        with col3:
            video_count = channel_info['video_count']
            st.header("  Total Videos  ")
            st.subheader(video_count)

        with col4:
            channel_created_date = channel_info['channel_created_date']
            created_date = channel_created_date[:10]
            st.header("Channel Created ")
            st.subheader(created_date)

        with col5:
            st.header(" Subscriber_Count ")
            st.subheader(channel_info["subscriber_count"])

        st.title(" ")

        stats = get_video_stats(video_id)

        st.title("Video Information :")
        col6, col7, col8 = st.columns(3)

        with col6:
            st.header("  Total Views  ")
            st.subheader(stats["viewCount"])

        with col7:
            st.header(" Like Count ")
            st.subheader(stats["likeCount"])

        with col8:
            st.header(" Comment Count ")
            st.subheader(stats["commentCount"])

        st.header(" ")

        _, container, _ = st.columns([10, 80, 10])
        container.video(data=youtube_link)

        results = analyze_sentiment(csv_file)

        col9, col10, col11 = st.columns(3)

        with col9:
            st.header("  Positive Comments  ")
            st.subheader(results['num_positive'])

        with col10:
            st.header(" Negative Comments ")
            st.subheader(results['num_negative'])

        with col11:
            st.header(" Neutral Comments ")
            st.subheader(results['num_neutral'])

        bar_chart(csv_file)
        plot_sentiment(csv_file)

        st.subheader("Channel Description ")
        channel_description = channel_info['channel_description']
        st.write(channel_description)

        st.title("Comments by Sentiment")

        positive_comments = []
        negative_comments = []
        neutral_comments = []

        sid = SentimentIntensityAnalyzer()

        with open(csv_file, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                comment = row['Comment']
                sentiment_scores = sid.polarity_scores(comment)
                if sentiment_scores['compound'] > 0.0:
                    positive_comments.append((row['Username'], comment))
                elif sentiment_scores['compound'] < 0.0:
                    negative_comments.append((row['Username'], comment))
                else:
                    neutral_comments.append((row['Username'], comment))

        st.title("Positive Comments")
        st.write("---")
        for username, comment in positive_comments:
            st.markdown(f"<span style='color:green'>**{username}:** {comment}</span>", unsafe_allow_html=True)
            st.write("---")

        st.title("Negative Comments")
        st.write("---")
        for username, comment in negative_comments:
            st.markdown(f"<span style='color:red'>**{username}:** {comment}</span>", unsafe_allow_html=True)
            st.write("---")

        st.title("Neutral Comments")
        st.write("---")
        for username, comment in neutral_comments:
            st.markdown(f"<span style='color:white'>**{username}:** {comment}</span>", unsafe_allow_html=True)
            st.write("---")
    else:
        st.error("Invalid YouTube link")


import csv
import re
import pandas as pd
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.express as px
import plotly.graph_objects as go
from colorama import Fore, Style
from typing import Dict
import streamlit as st

def extract_video_id(youtube_link):
    video_id_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(video_id_regex, youtube_link)
    if match:
        video_id = match.group(1)
        return video_id
    else:
        return None

def analyze_sentiment(csv_file):
    # Initialize the sentiment analyzer
    sid = SentimentIntensityAnalyzer()

    # Read in the YouTube comments from the CSV file
    comments = []
    with open(csv_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            comments.append(row['Comment'])

    # Count the number of neutral, positive, and negative comments
    num_neutral = 0
    num_positive = 0
    num_negative = 0
    for comment in comments:
        sentiment_scores = sid.polarity_scores(comment)
        if sentiment_scores['compound'] == 0.0:
            num_neutral += 1
        elif sentiment_scores['compound'] > 0.0:
            num_positive += 1
        else:
            num_negative += 1

    # Return the results as a dictionary
    results = {'num_neutral': num_neutral, 'num_positive': num_positive, 'num_negative': num_negative}
    return results

def bar_chart(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # Create a Pandas DataFrame with the results
    df = pd.DataFrame({
        'Sentiment': ['Positive', 'Negative', 'Neutral'],
        'Number of Comments': [num_positive, num_negative, num_neutral]
    })

    # Create the bar chart using Plotly Express
    fig = px.bar(df, x='Sentiment', y='Number of Comments', color='Sentiment', 
                 color_discrete_sequence=['#87CEFA', '#FFA07A', '#D3D3D3'],
                 title='Sentiment Analysis Results')
    fig.update_layout(title_font=dict(size=20))


    # Show the chart
    st.plotly_chart(fig, use_container_width=True)    
    
def plot_sentiment(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # Plot the pie chart
    labels = ['Neutral', 'Positive', 'Negative']
    values = [num_neutral, num_positive, num_negative]
    colors = ['yellow', 'green', 'red']
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent',
                                 marker=dict(colors=colors))])
    fig.update_layout(title={'text': 'Sentiment Analysis Results', 'font': {'size': 20, 'family': 'Arial', 'color': 'grey'},
                              'x': 0.5, 'y': 0.9},
                      font=dict(size=14))
    st.plotly_chart(fig)
    
    
    
def create_scatterplot(csv_file: str, x_column: str, y_column: str) -> None:
    # Load data from CSV
    data = pd.read_csv(csv_file)

    # Create scatter plot using Plotly
    fig = px.scatter(data, x=x_column, y=y_column, color='Category')

    # Customize layout
    fig.update_layout(
        title='Scatter Plot',
        xaxis_title=x_column,
        yaxis_title=y_column,
        font=dict(size=18)
    )

    # Display plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    
    
def print_sentiment(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

  
    # Determine the overall sentiment
    if num_positive > num_negative:
        overall_sentiment = 'POSITIVE'
        color = Fore.GREEN
    elif num_negative > num_positive:
        overall_sentiment = 'NEGATIVE'
        color = Fore.RED
    else:
        overall_sentiment = 'NEUTRAL'
        color = Fore.YELLOW

    # Print the overall sentiment in color
    print('\n'+ Style.BRIGHT+ color + overall_sentiment.upper().center(50, ' ') + Style.RESET_ALL)



