import json
import pandas as pd
import numpy as np

def load_codebook(json_path):
    """Load codebook JSON file and return it as a dict."""
    with open(json_path, 'r') as file:
        return json.load(file)

def load_raw(tsv_path):
    """Load TSV file into a pandas DataFrame."""
    return pd.read_csv(tsv_path, sep='\t')

def decode_categorical(df, column, codebook_entry):
    """Map codes in a column to their string labels from codebook"""
    codes = codebook_entry['codes']
    mapping = {int(key): value for key, value in codes.items()}
    df[column] = df[column].map(mapping)
    return df

def clean_continuous(df, column, sentinels):
    """Replace sentinel values with NaN in a continuous variable."""
    df[column] = df[column].replace(sentinels, np.nan)
    return df
