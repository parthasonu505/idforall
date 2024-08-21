import pandas as pd
import sqlite3 
import numpy as np
import ftplib
conn = sqlite3.connect('data.db')
c = conn.cursor()
import streamlit as st
import random
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
index=None
value=[]
if 'go' not in st.session_state:
    st.session_state.go = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None
def change_go():
    if st.session_state.go:
        st.session_state.go=False
    else:
        st.session_state.go=True

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter Data on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                )
                df = df[df[column].isin(user_cat_input)]
                # user_text_input = right.text_input(
                #     f"Substring or regex in {column}",
                # )
                # if user_text_input:
                #     df = df[df[column].str.contains(user_text_input)]
    st.session_state.filtered_df=df
    return df

st.sidebar.title('Data Entry')
school_name = st.sidebar.text_input("Please Enter The Organization Code", "12345")
uploaded_file = st.sidebar.file_uploader("Choose a file", type = 'CSV')

if uploaded_file is not None:
    if st.session_state.df is None:
        print("****************hi*****************")
        #st.session_state.df = pd.read_excel(uploaded_file, sheet_name='Sheet1').fillna('NULL')
        st.session_state.df=pd.read_csv(uploaded_file).fillna('NULL')
if st.session_state.df is not None:
    st.dataframe(filter_dataframe(st.session_state.df ))
    st.button('Go', on_click=change_go)
r1c1,r1c2 = st.columns([2,2])
with r1c1:
    if(st.session_state.go):
        index=list(st.session_state.filtered_df.index)[0]
        if('photo_taken' in st.session_state.df.columns):
            option = st.selectbox('How would you like submit photo',('Capture', 'Upload'))
            if(option == 'Capture'):
                picture = st.camera_input("Take a picture")
                st.session_state.df["photo_name"][index]=f"{st.session_state.df[st.session_state.df.columns[0]][index]}_{st.session_state.df[st.session_state.df.columns[1]][index]}_{st.session_state.df[st.session_state.df.columns[2]][index]}_{random.randint(1, 99999)}_photo.jpg"
                st.session_state.df["photo_taken"][index]="Yes"
            else:
                picture = st.file_uploader("Upload a picture", type = 'jpg')
                if picture:
                    st.image(picture, caption='Uploaded Photo')
                    st.session_state.df["photo_name"][index]=f"{st.session_state.df[st.session_state.df.columns[0]][index]}_{st.session_state.df[st.session_state.df.columns[1]][index]}_{st.session_state.df[st.session_state.df.columns[2]][index]}_{random.randint(1, 99999)}_photo.jpg"
                st.session_state.df["photo_taken"][index]="Yes"
        if('sign_taken' in st.session_state.df.columns):
            sign = st.file_uploader("Upload your signature", type = 'jpg')
            if sign:
                st.image(sign, caption='Uploaded Signature')
                st.session_state.df["sign_name"][index]=f"{st.session_state.df[st.session_state.df.columns[0]][index]}_{st.session_state.df[st.session_state.df.columns[1]][index]}_{st.session_state.df[st.session_state.df.columns[2]][index]}_{random.randint(1, 99999)}_sign.jpg"
                st.session_state.df["sign_taken"][index]="Yes"
with r1c2:
    if(st.session_state.go):
        index=list(st.session_state.filtered_df.index)[0]
        st.session_state.options=st.session_state.filtered_df.columns
        for i in st.session_state.options:
            value.append(st.text_input(i,st.session_state.df[i][index] ))
        if st.button("Submit"):
            field=['OrgID']
            vals=[str(school_name)]
            for i in range(len(value)):
                field.append(st.session_state.options[i])
                vals.append(value[i])
                st.session_state.df[st.session_state.options[i]][index]=value[i]
            table_name=f"Data_{school_name}_table"
            print("query: ",f'INSERT INTO {table_name}{tuple(field)} VALUES {tuple(vals)}')
            c.execute(f'INSERT INTO {table_name}{tuple(field)} VALUES {tuple(vals)}')
            conn.commit()
            st.dataframe(st.session_state.df )
            # Connect FTP Server
            ftp_server = ftplib.FTP('ftp.digidemy.in', 'u669719505.partha', 'Partha123$#@')
            
            # force UTF-8 encoding
            ftp_server.encoding = "utf-8"
            
            # Enter File Name with Extension
            filename = "data.db"
            
            # Read file in binary mode
            with open(filename, "rb") as file:
            	# Command for Uploading the file "STOR filename"
            	ftp_server.storbinary(f"STOR {filename}", file)
            
            # Close the Connection
            ftp_server.quit()
        

