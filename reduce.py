from dataclasses import replace
import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
#engine = create_engine('sqlite://', echo=False)

CON = sqlite3.connect(os.path.expanduser("C:\GitHub\TLars\crec.db"))

CUR = CON.cursor()


MAIN_KEYWORD = r'climate\schange|global\swarming' # Reduce full db to keywords



def df_main():
    """Pull full database into dataframe"""
    crec_df = pd.read_sql("Select * from crec", CON, index_col='UTC')
    crec_df['html_data'] = crec_df['html_data'].str.replace('\n', ' ')
    #crec_df = crec_df.set_index(pd.DatetimeIndex(crec_df.index)).loc[:'2016-01-01'] # (End Date?) Control date range of df
    #crec_df.drop(['2016-02-30', '2016-02-31'])
    return crec_df


def df_reduce():
    """Pull database reduced by MAIN_KEYWORD into dataframe"""
    """Going to reduce database further by ignoring stopwords"""
    df_reduced = df_main()[df_main()['html_data'].str.contains(MAIN_KEYWORD)] 
    df_reduced.to_sql('Reduced', CON, if_exists='replace')

    return df_reduced

df_reduce()