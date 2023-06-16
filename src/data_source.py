from pathlib import Path

import pandas as pd
import streamlit as st

# Example of a data source

DATA_FILE = "data/TODO.parquet"  # e.g. created in notebooks/data-elt.ipynb


@st.cache_data
def load_data():
    if Path(DATA_FILE).exists():
        return pd.read_parquet(DATA_FILE)
    else:
        return None
        # raise FileNotFoundError
