import streamlit as st
import pandas as pd

from data_source import load_data

st.header("TODO: Explore Data")

df = load_data()

if df is not None:
    st.write(df)
else:
    st.warning("No data found")
