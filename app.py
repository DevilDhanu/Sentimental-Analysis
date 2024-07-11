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