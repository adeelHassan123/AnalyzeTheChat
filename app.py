import pandas as pd
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
import streamlit as st # type: ignore
from preprocessor import preprocess
from utils import (
    fetch_stats, fetch_most_active_users, generate_wordcloud, 
    fetch_most_common_words, fetch_emoji_stats, monthly_timeline, 
    daily_timeline, week_activity_map, month_activity_map, activity_heatmap
)
import emoji # type: ignore

# Custom CSS for futuristic theme
st.markdown("""
    <style>
    /* General app styling */
    .stApp {
        background: linear-gradient(135deg, #2B0B3A 0%, #1A0B3A 100%);
        color: #E0E0E0;
        font-family: 'Poppins', sans-serif;
    }
    /* Glassmorphism card styling */
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
    }
    /* Sidebar styling */
    .css-1lcbmhc {
        background: linear-gradient(180deg, #3A0B5A 0%, #1A0B3A 100%);
        border-right: 1px solid #00F4FF;
    }
    .stSidebar .stButton>button {
        background: linear-gradient(45deg, #00F4FF, #FF00FF);
        color: #FFFFFF;
        border-radius: 10px;
        border: none;
        padding: 12px;
        font-weight: 600;
        transition: background 0.3s ease;
    }
    .stSidebar .stButton>button:hover {
        background: linear-gradient(45deg, #00C4CC, #CC00CC);
    }
    /* Headers with neon glow */
    h1, h2, h3, h4 {
        color: #00F4FF;
        text-shadow: 0 0 5px #00F4FF, 0 0 10px #FF00FF;
        font-weight: 700;
    }
    /* Metrics */
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #00F4FF;
    }
    .stMetric label {
        color: #FF00FF;
        font-weight: 600;
    }
    .stMetric .css-1xarl3l {
        color: #E0E0E0;
        font-size: 1.2em;
    }
    /* Info and error messages */
    .stAlert {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #00F4FF;
        border-radius: 10px;
        color: #E0E0E0;
        padding: 10px;
    }
    /* Dataframe */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border: 1px solid #00F4FF;
    }
    /* Animation for cards */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .card {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
""", unsafe_allow_html=True)

# Streamlit app configuration
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    layout="wide",
    page_icon="💬"
)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>💬 Chat Analyzer</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📁 Upload file", type=["txt"], key="file_uploader")

# File loading
USE_LOCAL_FILE = False
chat_data = None
if uploaded_file is not None:
    chat_data = uploaded_file.read().decode("utf-8")
    USE_LOCAL_FILE = False
elif USE_LOCAL_FILE:
    try:
        with open("xyz.txt", "r", encoding="utf-8") as file:
            chat_data = file.read()
    except FileNotFoundError:
        st.sidebar.error("❌ 'chat_data.txt' not found.")

# Main app
st.markdown("<h1 style='text-align: center;'>📊 WhatsApp Chat Analyzer</h1>", unsafe_allow_html=True)

if chat_data:
    df = preprocess(chat_data)
    if df.empty:
        st.error("⚠️ No valid messages found. Expected format: 'DD/MM/YYYY, HH:MM AM/PM - User: Message'")
    else:
        df = df[df['user'] != 'Group_Message']
        if df.empty:
            st.warning("⚠️ All messages are group notifications. No user messages found.")
        
        # User filter
        with st.sidebar:
            unique_users = df['user'].unique().tolist()
            unique_users.sort()
            unique_users.insert(0, "Overall")
            selected_user = st.selectbox("👤 Select user", unique_users, key="user_select")
            if st.button("🔍 Analyze", key="analyze_button"):
                st.session_state.analyze_clicked = True
        
        # Insights
        if st.session_state.get("analyze_clicked", False):
            with st.container():
                st.markdown(f"<div class='card'><h3>📬 Messages from: {selected_user}</h3>", unsafe_allow_html=True)
                filtered_df = df if selected_user == "Overall" else df[df['user'] == selected_user]
                
                if filtered_df.empty:
                    st.error(f"⚠️ No messages found for {selected_user}. Try 'Overall' or check data.")
                else:                    
                    # Stats
                    st.markdown("<h3>📈 Statistics</h3>", unsafe_allow_html=True)
                    num_messages, total_words, num_media_messages, num_urls = fetch_stats(filtered_df)
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Messages", num_messages)
                    with col2:
                        st.metric("Words", total_words)
                    with col3:
                        st.metric("Media", num_media_messages)
                    with col4:
                        st.metric("URLs", num_urls)
                    
                    # Most active users
                    if selected_user == "Overall":
                        st.markdown("<div class='card'><h3>👥 Top Users</h3>", unsafe_allow_html=True)
                        top_users, user_percentage_df = fetch_most_active_users(df)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 🔢 Message Share (%)", unsafe_allow_html=True)
                            st.dataframe(user_percentage_df, use_container_width=True)
                        with col2:
                            st.markdown("#### 📊 Message Count", unsafe_allow_html=True)
                            fig = go.Figure(data=[
                                go.Bar(
                                    x=top_users.index, y=top_users.values, orientation='v',
                                    marker=dict(
                                        color=top_users.values,
                                        colorscale='Plasma',
                                        showscale=True,
                                        colorbar=dict(title="Messages"),
                                        line=dict(color='#00F4FF', width=2)
                                    ),
                                    hovertemplate="%{y}: %{x} messages<extra></extra>"
                                )
                            ])
                            fig.update_layout(
                                title="Top 5 Most Active Users",
                                xaxis_title="Messages", yaxis_title="Users",
                                template='plotly_dark', title_font=dict(size=16),
                                margin=dict(t=60, b=40), showlegend=False
                            )
                            st.plotly_chart(fig, use_container_width=True, key="most_active_users_chart")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Wordcloud
                    st.markdown("<div class='card'><h3>🌐 Word Cloud</h3>", unsafe_allow_html=True)
                    wordcloud = generate_wordcloud(filtered_df)
                    if wordcloud:
                        st.image(wordcloud, use_container_width=True)
                    else:
                        st.info("No words found for word cloud.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Most common words
                    st.markdown("<div class='card'><h3>📚 Top 20 Words</h3>", unsafe_allow_html=True)
                    word_counts = fetch_most_common_words(filtered_df).head(10)
                    if not word_counts.empty:
                        top_words = word_counts.head(20)
                        fig = go.Figure(data=[
                            go.Bar(
                                x=top_words["count"], y=top_words["word"], orientation='h',
                                marker=dict(
                                    color=top_words["count"],
                                    colorscale='Viridis',
                                    showscale=True,
                                    colorbar=dict(title="Frequency"),
                                    line=dict(color='#FF00FF', width=2)
                                ),
                                hovertemplate="%{y}: %{x} times<extra></extra>"
                            )
                        ])
                        fig.update_layout(
                            title="Top 20 Most Frequent Words",
                            xaxis_title="Frequency", yaxis_title="Word",
                            template='plotly_dark', title_font=dict(size=20),
                            margin=dict(t=60, b=40), height=600, showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True, key="common_words_chart")
                    else:
                        st.info("No words found to display.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Emoji stats
                    st.markdown("<div class='card'><h3>😊 Top 20 Emojis</h3>", unsafe_allow_html=True)
                    emoji_counts = fetch_emoji_stats(filtered_df).head(10)
                    if not emoji_counts.empty:
                        top_emojis = emoji_counts.head(20)
                        fig = go.Figure(data=[
                            go.Bar(
                                x=top_emojis["count"], y=top_emojis["emoji"], orientation='h',
                                marker=dict(
                                    color=top_emojis["count"],
                                    colorscale='Hot',
                                    showscale=True,
                                    colorbar=dict(title="Frequency"),
                                    line=dict(color='#00FFAA', width=2)
                                ),
                                hovertemplate="%{y}: %{x} times<extra></extra>"
                            )
                        ])
                        fig.update_layout(
                            title="Top 20 Most Used Emojis",
                            xaxis_title="Frequency", yaxis_title="Emoji",
                            template='plotly_dark', title_font=dict(size=20),
                            margin=dict(t=60, b=40), height=600, showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True, key="emoji_stats_chart")
                    else:
                        st.info("No emojis found in the chat data.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Monthly timeline
                    st.markdown("<div class='card'><h3>📅 Monthly Timeline</h3>", unsafe_allow_html=True)
                    timeline = monthly_timeline(filtered_df)
                    if not timeline.empty:
                        fig = px.area(
                            timeline, x='time', y='message',
                            title=f"Messages per Month ({selected_user})",
                            labels={'time': 'Month-Year', 'message': 'Message Count'},
                            template='plotly_dark',
                            color_discrete_sequence=['#00F4FF']
                        )
                        fig.update_traces(
                            line=dict(width=3),
                            fill='tozeroy',
                            hovertemplate="%{x}: %{y} messages<extra></extra>"
                        )
                        fig.update_layout(
                            xaxis_title="Month-Year", yaxis_title="Messages",
                            title_font=dict(size=20), xaxis_tickangle=45, height=500,
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True, key="monthly_timeline_chart")
                    else:
                        st.info(f"No data available for monthly timeline for {selected_user}.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Daily timeline
                    st.markdown("<div class='card'><h3>📆 Daily Timeline</h3>", unsafe_allow_html=True)
                    daily_timeline_data = daily_timeline(filtered_df)
                    if not daily_timeline_data.empty:
                        fig = px.area(
                            daily_timeline_data, x='only_date', y='message',
                            title=f"Messages per Day ({selected_user})",
                            labels={'only_date': 'Date', 'message': 'Message Count'},
                            template='plotly_dark',
                            color_discrete_sequence=['#FF00FF']
                        )
                        fig.update_traces(
                            line=dict(width=3),
                            fill='tozeroy',
                            hovertemplate="%{x|%Y-%m-%d}: %{y} messages<extra></extra>"
                        )
                        fig.update_layout(
                            xaxis_title="Date", yaxis_title="Messages",
                            title_font=dict(size=20), xaxis_tickangle=45, height=500,
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True, key="daily_timeline_chart")
                    else:
                        st.info(f"No data available for daily timeline for {selected_user}.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Activity map
                    st.markdown("<div class='card'><h3>📊 Activity Map</h3>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### Most Active Day", unsafe_allow_html=True)
                        busy_day = week_activity_map(filtered_df)
                        if busy_day.sum() > 0:
                            fig = go.Figure(data=[
                                go.Bar(
                                    x=busy_day.index, y=busy_day.values,
                                    marker=dict(
                                        color=busy_day.values,
                                        colorscale='Teal',
                                        showscale=True,
                                        colorbar=dict(title="Messages"),
                                        line=dict(color='#00FFAA', width=2)
                                    ),
                                    hovertemplate="%{x}: %{y} messages<extra></extra>"
                                )
                            ])
                            fig.update_layout(
                                title="Messages by Day of Week",
                                xaxis_title="Day", yaxis_title="Messages",
                                template='plotly_dark', title_font=dict(size=16),
                                xaxis_tickangle=45, showlegend=False
                            )
                            st.plotly_chart(fig, use_container_width=True, key="activity_day_chart")
                        else:
                            st.info(f"No data available for day activity for {selected_user}.")
                    
                    with col2:
                        st.markdown("#### Most Active Month", unsafe_allow_html=True)
                        busy_month = month_activity_map(filtered_df)
                        if busy_month.sum() > 0:
                            fig = go.Figure(data=[
                                go.Bar(
                                    x=busy_month.index, y=busy_month.values,
                                    marker=dict(
                                        color=busy_month.values,
                                        colorscale='Portland',
                                        showscale=True,
                                        colorbar=dict(title="Messages"),
                                        line=dict(color='#FF00FF', width=2)
                                    ),
                                    hovertemplate="%{x}: %{y} messages<extra></extra>"
                                )
                            ])
                            fig.update_layout(
                                title="Messages by Month",
                                xaxis_title="Month", yaxis_title="Messages",
                                template='plotly_dark', title_font=dict(size=16),
                                xaxis_tickangle=45, showlegend=False
                            )
                            st.plotly_chart(fig, use_container_width=True, key="activity_month_chart")
                        else:
                            st.info(f"No data available for month activity for {selected_user}.")
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Activity Heatmap
                    st.markdown("<div class='card'><h3>🔥 Activity Heatmap</h3>", unsafe_allow_html=True)
                    heatmap_data = activity_heatmap(filtered_df)
                    if not heatmap_data.empty and heatmap_data.values.sum() > 0:
                        fig = px.imshow(
                            heatmap_data,
                            x=list(heatmap_data.columns),
                            y=list(heatmap_data.index),
                            labels=dict(x="Hour of Day", y="Day of Week", color="Messages"),
                            title=f"Message Activity Heatmap ({selected_user})",
                            text_auto=True,  # optional: shows message counts in each cell
                            color_continuous_scale=[
                                [0, '#000000'], [0.2, '#00F4FF'], [0.5, "#86D821"], [1, "#FF0000"]
                            ],
                            template='plotly_dark'
                        )
                        fig.update_layout(
                            title=f"Message Activity Heatmap ({selected_user})",
                            title_font=dict(size=20),
                            xaxis=dict(type='category'),  # 🚨 Force x-axis to treat labels as categories
                            height=500
                        )
                        fig.update_traces(
                            hovertemplate="%{y}, %{x}: %{z} messages<extra></extra>",
                            zmin=0, zmax=heatmap_data.values.max(),
                            showscale=True
                        )
                        st.plotly_chart(fig, use_container_width=True, key="weekly_heatmap_chart")
                    else:
                        st.info(f"No data available for activity heatmap for {selected_user}.")
                    st.markdown("</div>", unsafe_allow_html=True)
     
else:
    st.info("👈 Upload a chat file to analyze it.")
    st.markdown("**Expected format**: `12/31/2024, 11:59 PM - User: Message`")

# Footer
st.markdown("<div style='text-align: center; color: #00FFAA; margin-top: 20px;'>Made with ❤️ by Adeel Hassan (<a href='https://github.com/adeelHassan123' style='color: #00F4FF;'>GitHub</a>)</div>", unsafe_allow_html=True)
