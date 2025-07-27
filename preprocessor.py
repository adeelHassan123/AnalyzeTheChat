import pandas as pd
import re
import streamlit as st # type: ignore

# ---------------- PREPROCESS FUNCTION ----------------
# ---------------- PREPROCESS FUNCTION ----------------
def preprocess(chat_data):
    # Corrected pattern with narrow non-breaking space (u202f) before am/pm
    date_time_pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}[\u202f ]?(?i:am|pm)\s*-\s*'
    msg_list = re.split(date_time_pattern, chat_data)[1:]
    date_list = re.findall(date_time_pattern, chat_data)
    
    # Clean the date strings
    cleaned_dates = [d.replace('\u202f', '').replace('am', 'AM').replace('pm', 'PM') for d in date_list]
    
    df = pd.DataFrame({'msg_raw': msg_list, 'dt_raw': cleaned_dates})
    
    # Convert to datetime with 12-hour format
    df['dt_raw'] = pd.to_datetime(df['dt_raw'], format='%d/%m/%Y, %I:%M%p - ', errors='coerce')
    df.rename(columns={'dt_raw': 'date'}, inplace=True)
    
    # Separate user and message
    user_names = []
    actual_msgs = []
    for msg in df['msg_raw']:
        split_msg = re.split(r'([\w\W]+?): ', msg)
        if len(split_msg) > 2:
            user_names.append(split_msg[1])
            actual_msgs.append(' '.join(split_msg[2:]))
        else:
            user_names.append('Group_Message')
            actual_msgs.append(msg)
    
    df['user'] = user_names
    df['message'] = actual_msgs
    df.drop(columns=['msg_raw'], inplace=True)
    
    # Extract date parts
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    
    # Create period column for heatmap
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour:02d}-00")
        elif hour == 0:
            period.append(f"00-01")
        else:
            period.append(f"{hour:02d}-{hour+1:02d}")
    df['period'] = period
    
    return df