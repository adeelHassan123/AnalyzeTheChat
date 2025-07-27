from wordcloud import WordCloud # type: ignore
from collections import Counter
import pandas as pd
import emoji # type: ignore
import streamlit as st # type: ignore

# ---------------- UTILS FUNCTIONS (Provided) ----------------
def fetch_stats(df):
    num_messages = df.shape[0]
    words = df['message'].str.split().apply(len).sum()
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    url_list = [i for i in df['message'] if i.startswith('https://') or i.startswith('http://')]
    num_urls = len(url_list)
    return num_messages, words, num_media_messages, num_urls

def fetch_most_active_users(df):
    top_users = df['user'].value_counts().head(5)
    user_percentage_df = (df['user'].value_counts(normalize=True) * 100).round(2).reset_index()
    user_percentage_df.columns = ['user', 'percentage']
    return top_users, user_percentage_df

def generate_wordcloud(df):
    try:
        with open("stop_words.txt", 'r') as f:
            stop_words = f.read().split()
    except FileNotFoundError:
        stop_words = []
        st.warning("⚠️ stop_words.txt not found. Proceeding without stop words.")
    df = df[df['message'] != '<Media omitted>\n']
    messages = df['message'].dropna().astype(str)
    if not messages.empty:
        wc = WordCloud(width = 3000, height = 2000, random_state=1, background_color='black', colormap='Set2', collocations=False, stopwords = stop_words)
        df_wc = wc.generate(' '.join(messages))
        return df_wc.to_image()
    return None

def fetch_most_common_words(df):
    temp = df[df['message'] != '<Media omitted>\n']
    temp = temp[temp['user'] != 'Group_Message']
    temp = temp[temp['message'] != 'This message was deleted\n']
    try:
        with open("stop_words.txt", 'r') as f:
            stop_words = f.read().split()
    except FileNotFoundError:
        stop_words = []
        st.warning("⚠️ stop_words.txt not found. Proceeding without stop words.")
    
    msg = []
    for message in temp['message']:
        for word in message.split():
            i = word.lower().strip('.,!?()[]{}"\'')
            if i and i not in stop_words:
                msg.append(i)
    
    return pd.DataFrame(Counter(msg).most_common(50), columns=['word', 'count'])

def fetch_emoji_stats(df):
    emoji_list = []
    for msg in df['message']:
        emoji_list.extend([c for c in msg if c in emoji.EMOJI_DATA])
    emoji_df = pd.DataFrame(emoji_list, columns=['emoji'])
    emoji_counts = emoji_df['emoji'].value_counts().reset_index(name='count')
    emoji_counts.columns = ['emoji', 'count']
    return emoji_counts.head(50)

def monthly_timeline(df):
    if df.empty:
        return pd.DataFrame()
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'].str[:3] + "-" + timeline['year'].astype(str)
    return timeline

def daily_timeline(df):
    if df.empty:
        return pd.DataFrame()
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    daily_timeline['only_date'] = pd.to_datetime(daily_timeline['only_date'], errors='coerce')
    return daily_timeline.dropna()

def week_activity_map(df):
    if df.empty:
        return pd.Series()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return df['day_name'].value_counts().reindex(day_order, fill_value=0)

def month_activity_map(df):
    if df.empty:
        return pd.Series()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    return df['month'].value_counts().reindex(month_order, fill_value=0)

def activity_heatmap(df):
    if df.empty:
        return pd.DataFrame()
    # Ensure correct order of days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # Pivot: day vs hour range
    user_heatmap = df.pivot_table(
        index='day_name',
        columns='period',
        values='message',  # Or 'message_id' if messages aren't strings
        aggfunc='count',
        fill_value=0
    )
    # Reorder days
    user_heatmap = user_heatmap.reindex(day_order, fill_value=1)
    # Sort hour ranges properly (like '0-1', '1-2', ...)
    user_heatmap = user_heatmap[sorted(user_heatmap.columns, key=lambda x: int(x.split('-')[0]))]
    return user_heatmap
