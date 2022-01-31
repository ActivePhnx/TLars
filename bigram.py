import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from nltk.corpus import stopwords
import re

stop = stopwords.words('english')


CON = sqlite3.connect(os.path.expanduser(
    "C:\GitHub\TLars\crec.db"))

CUR = CON.cursor()


MAIN_KEYWORD = r'climate\schange|global\swarming' # Reduce full db to keywords


def df_main():
    """Pull full database into dataframe"""
    reduced_df = pd.read_sql("Select * from Reduced", CON, index_col='UTC')
    reduced_df['html_data'] = reduced_df['html_data'].str.replace('\n', ' ')
    #reduced_df = reduced_df.set_index(pd.DatetimeIndex(reduced_df.index)).loc[:'2021-12-31'] # (End Date?) Control date range of df
    return reduced_df


def df_clean():
    """Going to reduce database further by ignoring stopwords and punctuation"""
    clean_df = df_main()
    clean_df["html_data"].apply(lambda x : str.lower(x))
    #clean_df["html_data"].str.replace('[^\w\s]','')  Maybe?
    clean_df["html_data"].apply(lambda x : " ".join(re.findall('[\w]+',x)))
    #clean_df = df_main()['html_data'].apply(lambda x: [item for item in x if item not in stop])
    #clean_df['html_data'].apply(lambda x: [item for item in x if item not in stop])
    clean_df["html_data"].apply(lambda words: ' '.join(word.lower() for word in words.split() if word not in stop))
    return clean_df

df_clean().to_sql('clean', CON, if_exists='replace')