import streamlit as st
import pandas as pd
from urllib.parse import urlparse
from sqlalchemy import create_engine, text
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.colored_header import colored_header
from math import ceil
from st_aggrid import AgGrid, GridOptionsBuilder

#config
host = st.secrets.HOST
port = st.secrets.PORT
b2b_database = st.secrets.B2B_DB
user = st.secrets.USER
password = st.secrets.PASSWORD

st.set_page_config(
    page_title="B2B Company Data",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

colored_header(
    label='🏢 Find Your Ideal B2B Customers',
    description= ' Get Accurate Company Data',
    color_name= 'yellow-80'
)

if 'access' not in st.session_state:
    st.session_state['access'] = False


if 'country' not in st.session_state:
    st.session_state['country'] = None
if 'data' not in st.session_state:
    st.session_state['data'] = None

#get the engine
@st.cache_resource
def b2b_get_engine():
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{b2b_database}")
    return engine

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

#get_all_data from database
def get_all_data(table):
    engine = b2b_get_engine()
    query = text(f'SELECT * FROM {table}')
    df = pd.read_sql_query(query, engine.connect())
    engine.dispose()
    return df

#function to get the new dataframe with clean domains
def get_new_df(df):
    new_df = df[['Company', 'Website', 'Company Country', 'Short Description']]
    new_df = new_df.dropna()
    new_df =  new_df[~new_df['Website'].str.contains('facebook.com')]
    new_df = new_df.drop_duplicates()
    new_df = new_df.drop_duplicates(subset=['Website'])
    return new_df

def main():
    if 'pagenumber' not in st.session_state:
        st.session_state['pagenumber'] = 0
    table = st.selectbox('Choose Database', ('travel_agency', 'travel_booking_sites', 
    'concert_tour_companies', 'travel_insurance', 'event_coordinators', 'taxi_companies',
    'car_rental', 'tour_operators', 'tourism_association', 'airlines', 'cruise_ship',
    'travel_publication'))
    if st.button('Search!'):
        if 'dataframe' in st.session_state:
            del st.session_state['dataframe']
        if 'dataframe' not in st.session_state:
            dataframe = get_all_data(table)
            st.session_state['dataframe'] = dataframe
    prev, total_data ,next = st.columns([1, 10, 1])
    try:
        new_df = get_new_df(st.session_state['dataframe'])
        total_data.success(len(new_df))
        N = 100
        last_page = len(new_df) // N
        if next.button("Next"):
            if st.session_state['pagenumber'] + 1 > last_page:
                st.session_state['pagenumber'] = 0
            else:
                st.session_state['pagenumber'] += 1

        if prev.button("Prev"):
            if st.session_state['pagenumber'] - 1 < 0:
                st.session_state['pagenumber'] = last_page
            else:
                st.session_state['pagenumber'] -= 1
        # Get start and end indices of the next page of the dataframe
        start_idx = st.session_state['pagenumber'] * N 
        end_idx = (1 + st.session_state['pagenumber']) * N
        df_to_display = dataframe_explorer(new_df.iloc[start_idx:end_idx])
        st.dataframe(df_to_display, use_container_width=True)

        csv = convert_df(new_df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'{table}_company.csv',
            mime='text/csv',
        )
    except:
        st.stop()
            
if st.session_state['access']:
    main()
else:
    st.warning('Go to Homepage to login before you can get B2B Company Data')


    