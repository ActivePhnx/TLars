from dataclasses import replace
import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
#engine = create_engine('sqlite://', echo=False)

CON = sqlite3.connect(os.path.expanduser("C:\GitHub\TLars\crec.db"))

CUR = CON.cursor()


MAIN_KEYWORD = r'climate\schange|global\swarming' # Reduce full db to keywords

"""Pull full database into dataframe"""
crec_df = pd.read_sql("Select * from bigrams", CON)

crec_df.to_excel('bigrams.xlsx')