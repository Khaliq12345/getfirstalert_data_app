import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.colored_header import colored_header

#config
host = st.secrets.HOST
port = st.secrets.PORT
inf_database = st.secrets.inf_DB
user = st.secrets.USER
password = st.secrets.PASSWORD

st.set_page_config(
    page_title="Influencers Data",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

colored_header(
    label='🎯 Get Accurate Influencer Data',
    description= 'Find the Right Influencers for Your Business',
    color_name= 'violet-70'
)

#get the engine
@st.cache_resource
def inf_get_engine():
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{inf_database}")
    return engine

#get_all_data from database
def get_all_data(table):
    engine = inf_get_engine()
    query = text(f'SELECT * FROM {table}')
    df = pd.read_sql_query(query, engine.connect())
    engine.dispose()
    return df

#function to get the new dataframe with clean domains
def get_new_df(df):
    new_df = df[['Platform', 'Username', 'Name', 'Email', 'followers', 'Bio', 'Location']]
    new_df = new_df.dropna(how='any')
    new_df = new_df.drop_duplicates()
    new_df = new_df.drop_duplicates(subset=['Username'])
    return new_df

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

if 'access' not in st.session_state:
    st.session_state['access'] = False

def main():
    table = st.selectbox('Choose Database', ('travel_blogger', 'travel_addict', 
    'travel_blog', 'traveller', 'travelphotographer', 'vacation','tourism'))
    if st.button('Search!'):
        if 'inf_dataframe' in st.session_state:
            del st.session_state['inf_dataframe']
        if 'inf_dataframe' not in st.session_state:
            inf_dataframe = get_all_data(table)
            st.session_state['inf_dataframe'] = inf_dataframe
    try:
        new_df = get_new_df(st.session_state['inf_dataframe'])      
        new_df = dataframe_explorer(new_df)
        st.dataframe(new_df, use_container_width=True)

        csv = convert_df(new_df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'{table}_influencer.csv',
            mime='text/csv',
        )
    except:
        st.stop()
            
if st.session_state['access']:
    main()
else:
    st.warning('Go to Homepage and login before you can get Influencers Data')