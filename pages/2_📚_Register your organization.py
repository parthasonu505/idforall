import streamlit as st
import sqlite3 
import pandas as pd
import numpy as np
conn = sqlite3.connect('data.db')
c = conn.cursor()

st.cache_data

def convert_df(df):

    # IMPORTANT: Cache the conversion to prevent computation on every rerun

    return df.to_csv().encode('utf-8')

def create_usertable(options,org_id):
    tablename=f"Data_{org_id}_table"
    columnname="OrgID TEXT"
    for i in options:
        columnname+=','+i+' TEXT'
    print("hiiiiiiiiiiiiiiiiiii: ",f'CREATE TABLE IF NOT EXISTS {tablename}({columnname})')
    c.execute(f'CREATE TABLE IF NOT EXISTS {tablename}({columnname})')

if "User" in st.session_state:
    st.write(f"Welcome {st.session_state['User']}")
    org_id = st.text_input("Organizatiopn ID:")
    card_fields=['Name', 'Address', 'Phone', 'Class', 'Section', 'Roll', 'Code', 'Picture', 'Guardian_Number', 'Fathers_Name', 'Mothers_Name', 'Blood_Group','DOB','Employee_id','Session','Gender','Contact_No','Designation','Blood_Group']
    options = st.multiselect("Select the fields you want on your ID Card: ",card_fields)
    st.session_state.options = options
    addphoto = st.checkbox("Includ Photo")
    addsign = st.checkbox("Includ Sign")
    if st.button("Submit"):
        st.session_state["Orgid"]=org_id
        if addphoto:
            options.extend(["photo_taken","photo_name"])
        if addsign:
            options.extend(["sign_taken","sign_name"])
        create_usertable(options,org_id)
        st.write("Your Data Template: ")
        df = pd.DataFrame(columns=options)
        csv = convert_df(df)
        st.dataframe(df)
        st.download_button( label="Download Template as CSV",data=csv,file_name='Template.csv',mime='text/csv')
        #st.write("You selected:", options)
else:
    st.write("Please Login First")