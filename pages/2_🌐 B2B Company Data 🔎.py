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

#get a better dataframe
def cool_df(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=100)
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, editable=True)
    gb.configure_selection('multiple',header_checkbox=True)
    gb.configure_grid_options(enableRangeSelection = True)
    gridOptions = gb.build()
    return gridOptions

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

#function to clean the links
def clean_links(links):
    all_link = []
    for link in links:
        parsed_url = urlparse(link)
        domain_name = parsed_url.netloc
        all_link.append(domain_name)
    return all_link

#function to get the new dataframe with clean domains
def get_new_df(df):
    new_df = df[['Company', 'Website', 'Company Country', 'Short Description']]
    new_df = new_df.dropna()
    new_df =  new_df[~new_df['Website'].str.contains('facebook.com')]
    new_df = new_df.drop_duplicates()
    new_df['Website'] = clean_links(new_df['Website'].to_list())
    new_df = new_df.drop_duplicates(subset=['Website'])
    return new_df

def main():
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
    try:
        new_df = get_new_df(st.session_state['dataframe'])
        AgGrid(new_df, cool_df(new_df), width='200%')

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


    