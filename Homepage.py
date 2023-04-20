import streamlit as st
from streamlit_extras.colored_header import colored_header

if 'access' not in st.session_state:
    st.session_state['access'] = False

admin = st.secrets.ADMIN
pswd = st.secrets.PSWD

def login_app():
    st.set_page_config(
        page_title="Login",
        page_icon="🔑",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    colored_header(
        label='🔑 Login',
        description= 'Welcome back! Please enter your username and password to log in.',
        color_name= 'blue-green-70'
    )
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == admin and password == pswd:
            st.success("Logged in as {}".format(username))
            st.session_state['access'] = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

def access_app():
    st.set_page_config(
        page_title="Data",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    colored_header(
    label='📊 Data',
    description= 'Get Accurate and Reliable Data on Influencers and Leads',
    color_name= 'green-70'
    )
    
    st.success('Welcome!')

    st.write("""
# Welcome to our Streamlit data web app!

Our app is designed to provide you with all the information you need to make informed decisions about B2B companies, influencers, and email verification. With our easy-to-use platform, you can quickly and efficiently gather data on potential partners, influencers, and leads.

Our app is divided into three main sections:

1. **B2B Company Data:** This section allows you to search for and retrieve detailed information on B2B companies, including their industry, size, revenue, and contact information.

2. **Influencer Data:** In this section, you can find data on social media influencers, such as their number of followers, engagement rates, and audience demographics.

3. **Email Verification:** Our email verification tool helps you validate the accuracy of email addresses, ensuring that your messages reach the right people.

Our app is designed with user-friendliness in mind. You don't need any specialized technical skills to use it. Simply navigate to the section you need and enter your search parameters.

So why wait? Start exploring our Streamlit data web app today and take your business to the next level!
""")

    if st.button('Logout!'):
        st.session_state['access'] = False
        st.experimental_rerun()


if st.session_state['access']:
    access_app()
else:
    login_app()
