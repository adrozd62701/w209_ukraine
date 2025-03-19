import pandas as pd
import numpy as np
import streamlit as st

def load_data():
    data_path = 'data/Ukraine_Black_Sea_2020_2025_Jan24.csv.gz'
    data = pd.read_csv(data_path, compression='gzip')
    return data
