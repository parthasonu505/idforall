import streamlit as st

st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
)

st.title("Login Page")
# st.sidebar.success("Select a page above.")

# if "my_input" not in st.session_state:
#     st.session_state["my_input"] = ""

# my_input = st.text_input("Input a text here", st.session_state["my_input"])
# submit = st.button("Submit")
# if submit:
#     st.session_state["my_input"] = my_input
#     st.write("You have entered: ", my_input)

import pandas as pd
import hashlib

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False
# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT,mobile TEXT)')


def add_userdata(username,password,mobno):
    c.execute('INSERT INTO userstable(username,password,mobile) VALUES (?,?,?)',(username,password,mobno))
    conn.commit()

def login_user(username,password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
    data = c.fetchall()
    return data


def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data



def main():
    menu = ["Login","SignUp"]
    choice = st.selectbox("Menu",menu)
    if choice == "Login":
        st.subheader("Login Section")

        username = st.text_input("User Name")
        password = st.text_input("Password",type='password')
        if st.checkbox("Login"):
            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username,check_hashes(password,hashed_pswd))
            if result:

                st.success("Logged In as {}".format(username))
                st.session_state["User"] = username
                # task = st.selectbox("Task",["Add Post","Analytics","Profiles"])
                # if task == "Add Post":
                #     st.subheader("Add Your Post")

                # elif task == "Analytics":
                #     st.subheader("Analytics")
                # elif task == "Profiles":
                #     st.subheader("User Profiles")
                #     user_result = view_all_users()
                #     clean_db = pd.DataFrame(user_result,columns=["Username","Password"])
                #     st.dataframe(clean_db)
            else:
                st.warning("Incorrect Username/Password")





    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')
        mobile_no=st.text_input("Mobile No")
        if st.button("Signup"):
            create_usertable()
            add_userdata(new_user,make_hashes(new_password),mobile_no)
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")

main()