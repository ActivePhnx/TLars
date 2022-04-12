#!/usr/bin/env python3

import os
import re
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


CON = sqlite3.connect(os.path.expanduser(
    "C:\GitHub\TLars\crec.db"))

CUR = CON.cursor()

MAIN_KEYWORD = r'climate\schange|global\swarming' # Reduce full db to keywords

QUERY1 = r'\b(climate\schange|global\swarming)\W+(?:\w+\W+){0,150}?(fight(ing)?|(battle|battling)|must act|combat(ing)?|(struggle|struggling)|(oppose|opposing)|fight(ing)?\sback|defend(ing?)|press(ing)?|push(ing)?|campaign(ing)?)|(fight(ing)?|(battle|battling)|must act|combat(ing)?|(struggle|struggling)|(oppose|opposing)|fight(ing)?\sback|defend(ing?)|press(ing)?|push(ing)?|campaign(ing)?)\W+(?:\w+\W+){0,150}?(climate\schange|global\swarming)\b'
QUERY1_DESC = 'Active-agentic framing'

QUERY2 = r'\b(climate\schange|global\swarming)\W+(?:\w+\W+){0,150}?((examine|examining)|study(ing)?|assess(ing)?|model(ing)?|(measure|measuring)|(evaluate|evaluating)|(appraise|appraising))|((examine|examining)|study(ing)?|assess(ing)?|model(ing)?|(measure|measuring)|(evaluate|evaluating)|(appraise|appraising))\W+(?:\w+\W+){0,150}?(climate\schange|global\swarming)\b'
QUERY2_DESC = 'Passive-agentic framing'

def df_reduce():
    """Pull full database into dataframe"""
    crec_df = pd.read_sql("Select * from Reduced", CON, index_col='UTC')
    crec_df['html_data'] = crec_df['html_data'].str.replace('\n', ' ')
    crec_df = crec_df.set_index(pd.DatetimeIndex(crec_df.index)).id[:'2017-10-19'] # Control date range of df
    return crec_df


def df_map():
    """Move database to pandas df, reduce by keyword, and map by regex counts."""
    query1_compiled = re.compile(QUERY1, re.IGNORECASE)
    query2_compiled = re.compile(QUERY2, re.IGNORECASE)

    query1_list = []
    query2_list = []

    for chunk in pd.read_sql("Select * from crec", CON, index_col='UTC',
                             chunksize=1500):
        chunk['html_data'] = chunk['html_data'].str.replace('\n', ' ')
        chunk = chunk.set_index(pd.DatetimeIndex(chunk.index)).loc[:'2017-10-19']
        chunk = chunk[chunk.html_data.str.contains(MAIN_KEYWORD)]

        query1_list.append(pd.DataFrame(index=chunk.index,
                                        data=chunk.html_data.str.count(query1_compiled)))
        query2_list.append(pd.DataFrame(index=chunk.index,
                                        data=chunk.html_data.str.count(query2_compiled)))
    query1_df = pd.concat(query1_list)
    query2_df = pd.concat(query2_list)

    return query1_df, query2_df

def total_ratio():
    """Get ratio of all active-agentic:passive-agentic frames"""
    plot1_data, plot2_data = df_map()
    # ReSample data into quarters
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html#pandas.DataFrame.resample
    print(plot1_data.groupby(lambda x:x.year).sum())
    print(plot2_data.groupby(lambda x:x.year).sum())


def plot_frame():
    """Plot dataframes from regex_queries."""
    plot1_data, plot2_data = df_map()

    active_frame = []
    passive_frame = []
    ratio_list_frame = ([])
    # For Years TO for quarters in year
    for i in plot1_data.groupby([lambda x: x.year,lambda x: x.quarter]).sum().iterrows():
        active_frame.append(i[1].values)
    for i in plot2_data.groupby([lambda x: x.year,lambda x: x.quarter]).sum().iterrows():
        passive_frame.append(i[1].values)
    for ac, pa in zip(active_frame, passive_frame):
        ratio_list_frame.append(ac/pa)
    rounded_ratiolist_frame = [round(float(elem),3) for elem in
            ratio_list_frame]


    fig = plt.figure(figsize=(13,15))

    ax1 = plt.subplot(211)
    ax1.set_xlabel('Year', fontweight='bold')
    ax1.set_ylabel('Frequency', fontweight='bold')
    ax1.set_title('Agentic Frames in the Congressional Record', fontweight='bold', pad=15)
    print(type(plot2_data.index))
    plot2 = plt.bar(["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"] ,
                    plot2_data['html_data'].groupby([lambda x: x.year,lambda x: x.quarter]).sum(),
                    alpha=0.5, color="#6495ED")
    """plot1 = plt.bar(np.unique(plot1_data.index.year + 10000000),
                    plot1_data['html_data'].groupby([lambda x: x.year,lambda x: x.quarter]).sum(),
                    alpha=0.7, color="#FF5500", width=.4, align='edge')"""
    plot1 = plt.bar(["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"],
                    plot1_data['html_data'].groupby([lambda x: x.year,lambda x: x.quarter]).sum(),
                    alpha=0.7, color="#FF5500", width=.4, align='center')
    plt.legend((plot1, plot2, (plot1, plot2)), (QUERY1_DESC, QUERY2_DESC, 'Corpus-wide active/passive = {}'.format(
        round(sum(rounded_ratiolist_frame) / len(rounded_ratiolist_frame), 3))), loc=2, fontsize=17)

    ax1.annotate('', xy=(1995, -79), xytext=(2000, -79), arrowprops=dict(arrowstyle='<->', facecolor='black'),
                 annotation_clip=False)
    ax1.annotate('R. control', xy=(1997.5, -109), ha='center', annotation_clip=False)

    ax1.annotate('', xy=(2001, -79), xytext=(2002, -79), arrowprops=dict(arrowstyle='<->', facecolor='black'),
                 annotation_clip=False)
    ax1.annotate('D. control*', xy=(2001.5, -109), ha='center', annotation_clip=False)

    ax1.annotate('', xy=(2003, -79), xytext=(2006, -79), arrowprops=dict(arrowstyle='<->', facecolor='black'),
                 annotation_clip=False)
    ax1.annotate('R. control', xy=(2004.5, -109), ha='center', annotation_clip=False)

    ax1.annotate('', xy=(2007, -79), xytext=(2010, -79), arrowprops=dict(arrowstyle='<->', facecolor='black'),
                 annotation_clip=False)
    ax1.annotate('D. control', xy=(2008.5, -109), ha='center', annotation_clip=False)

    ax1.annotate('', xy=(2011, -79), xytext=(2014, -79), arrowprops=dict(arrowstyle='<->', facecolor='black'),
                 annotation_clip=False)
    ax1.annotate('Split control', xy=(2012.5, -109), ha='center', annotation_clip=False)

    ax1.annotate('', xy=(2015, -79), xytext=(2016, -79), arrowprops=dict(arrowstyle='<->', facecolor='black'),
                 annotation_clip=False)
    ax1.annotate('R. control', xy=(2015.5, -109), ha='center', annotation_clip=False)

    ax1.annotate('', xy=(1997.5, 140), xytext=(1996.5, 190), arrowprops=dict(arrowstyle='->', facecolor='black'),
                 annotation_clip=False)
    ax1.annotate('Kyoto protocol adopted', xy=(1995, 210), ha='center', annotation_clip=False)

    ax1.annotate('', xy=(2005, 360), xytext=(2004, 410), arrowprops=dict(arrowstyle='->', facecolor='black'),
                 annotation_clip=False)
    ax1.annotate('Kyoto protocol goes into effect', xy=(2002.5, 430), ha='center', annotation_clip=False)

    ax1.annotate('', xy=(2006, 140), xytext=(2006, 190), arrowprops=dict(arrowstyle='->', facecolor='black'),
                 annotation_clip=False)
    ax1.annotate('H.R. \n 5642', xy=(2006, 210), ha='center', annotation_clip=False)

    def autolabel_frames(rects):
        """
        Attach a text label above each bar displaying its height
        """
        for rect,item in zip(rects, rounded_ratiolist_frame):
            height = rect.get_height()
            ax1.text(rect.get_x() + rect.get_width()/2., 1.50+height,
                    item,
                    ha='center', va='bottom')
    autolabel_frames(plot2)


    fig.savefig('fig.png')


df_reduce()
df_map()
total_ratio()
plot_frame()