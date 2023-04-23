import streamlit as st
import pandas as pd
from pyisemail import is_email
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.colored_header import colored_header

st.set_page_config(
    page_title="Data Cleaning",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

colored_header(
    label='✅ Verify Your Leads and Emails',
    description= 'Get Accurate Data',
    color_name= 'red-70'
)

if 'access' not in st.session_state:
    st.session_state['access'] = False


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def is_valid(address):
    address = str(address)
    result = is_email(address, check_dns=True, allow_gtld=True)
    return result

def get_new_df(df):
    df = df[['person_first_name', 'person_last_name',
             'person_job_title', 'person_business_email', 'person_company_name',
             'person_phone']]
    #df['valid'] = df['person_business_email'].apply(is_valid)
    #df = df[df['valid'] == True]
    df = df.drop_duplicates(subset=['person_business_email'])
    return df

def main():
    if 'lead_pagenumber' not in st.session_state:
        st.session_state['lead_pagenumber'] = 0
    uploaded_file = st.file_uploader("Choose a file", type=['csv'])
    if uploaded_file is not None:
        dataframe = pd.read_csv(uploaded_file)
        if st.button('Clean'):
            if 'leads_dataframe' in st.session_state:
                del st.session_state['leads_dataframe']
            if 'leads_dataframe' not in st.session_state:
                dataframe = get_new_df(dataframe)
                st.session_state['leads_dataframe'] = dataframe
    prev, _ ,next = st.columns([1, 10, 1])
    try:
        new_df = st.session_state['leads_dataframe'] 
        N = 100
        last_page = len(new_df) // N
        if next.button("Next"):
            if st.session_state['lead_pagenumber'] + 1 > last_page:
                st.session_state['lead_pagenumber'] = 0
            else:
                st.session_state['lead_pagenumber'] += 1

        if prev.button("Prev"):
            if st.session_state['lead_pagenumber'] - 1 < 0:
                st.session_state['lead_pagenumber'] = last_page
            else:
                st.session_state['lead_pagenumber'] -= 1
        # Get start and end indices of the next page of the dataframe
        start_idx = st.session_state['lead_pagenumber'] * N 
        end_idx = (1 + st.session_state['lead_pagenumber']) * N
        df_to_display = dataframe_explorer(new_df.iloc[start_idx:end_idx])               
        st.dataframe(df_to_display, use_container_width=True)

        csv = convert_df(new_df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='lead.csv',
            mime='text/csv',
        )
    except:
        st.stop()

if st.session_state['access']:
    main()
else:
    st.warning('Go to Homepage to login before you can clean Leads data and Verify Emails')

