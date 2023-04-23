import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.colored_header import colored_header

#config
host = st.secrets.HOST
port = st.secrets.PORT
inf_database = st.secrets.INF_DB
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
    if 'inf_pagenumber' not in st.session_state:
        st.session_state['inf_pagenumber'] = 0
    table = st.selectbox('Choose Database', ('travel_blogger', 'travel_addict'
    , 'traveller', 'travelphotographer', 'vacation','tourism'))
    if st.button('Search!'):
        if 'inf_dataframe' in st.session_state:
            del st.session_state['inf_dataframe']
        if 'inf_dataframe' not in st.session_state:
            inf_dataframe = get_all_data(table)
            st.session_state['inf_dataframe'] = inf_dataframe
    prev, total_data ,next = st.columns([1, 10, 1])
    try:
        new_df = get_new_df(st.session_state['inf_dataframe'])
        total_data.success(len(new_df))  
        N = 100
        last_page = len(new_df) // N
        if next.button("Next"):
            if st.session_state['inf_pagenumber'] + 1 > last_page:
                st.session_state['inf_pagenumber'] = 0
            else:
                st.session_state['inf_pagenumber'] += 1

        if prev.button("Prev"):
            if st.session_state['inf_pagenumber'] - 1 < 0:
                st.session_state['inf_pagenumber'] = last_page
            else:
                st.session_state['inf_pagenumber'] -= 1
        # Get start and end indices of the next page of the dataframe
        start_idx = st.session_state['inf_pagenumber'] * N 
        end_idx = (1 + st.session_state['inf_pagenumber']) * N
        df_to_display = dataframe_explorer(new_df.iloc[start_idx:end_idx])    
        st.dataframe(df_to_display, use_container_width=True)

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