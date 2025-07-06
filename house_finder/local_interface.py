import streamlit as st
import pandas as pd
import numpy as np
import time
import search


# Using the "with" syntax

st.title('Real Estate Analysis App')
with st.form(key='my_form'):
    county = st.text_input('County',value="Temecula")
    max_price = st.number_input('Max Price',step=10000, value=700000)
    min_beds = st.number_input('Minimum Beds',step=1, value=3)
    min_baths = st.number_input('Minimum Bathrooms',step=.5,value=2.5)
    max_hoa = st.number_input('Max HOA',step=10,value=250)
    down_percent = st.number_input('Percentage Down',step=.01,value=.20)
    rate = st.number_input('Mortgage Rate',step=.0025,value=.0625, format="%0.4f")
    property_tax_rate = st.number_input('Property Tax Rate',step=.001,value=.011,  format="%0.3f")
    term_months = st.number_input('Loan term in months',step=1,value=360)

    num_properties = st.number_input('How many properties would you like to be displayed?',step=1,value=30)


    submit = st.form_submit_button('Begin Search')



if submit:
    df = None
    #  hoa=150, down_percent=0.20, rate=0.065, term_months=360, tax_rate = .011, num_properties = 2
    with st.spinner("searching, please wait"):
        df = search.main(county=county,
                         max_price=max_price, 
                         min_beds=min_beds, 
                         min_baths=min_baths,
                         hoa=max_hoa,
                         down_percent=down_percent,
                         rate=rate,
                         term_months=term_months,
                         tax_rate=property_tax_rate,
                         num_properties=num_properties,

                         )

    st.dataframe(df, use_container_width=True)
