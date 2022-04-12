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

QUERY1 = r'\b(climate\schange|global\swarming)\W+(?:\w+\W+){0,150}?(address(ing)?|combat(ing)?|fight(ing)?|act(ing)?|(mitigate|mgitigat(ing|ion)?)|(tackle|tackleing)|deal(ing)?|adapt(ing)?|confront(ing)?)\W+(?:\w+\W+){0,150}?(climate\schange|global\swarming)\b'
QUERY1_DESC = 'Active-agentic framing'

QUERY2 = r'\b(climate\schange|global\swarming)\W+(?:\w+\W+){0,150}?(talk(ing)?|(examine|examin(ing))|study(ing)?|access(ing)?|(measure|measuring)|model(ing)?|(evaluate|evaluating))\W+(?:\w+\W+){0,150}?(climate\schange|global\swarming)\b'
QUERY2_DESC = 'Passive-agentic framing'

QUERY3 = r'\b(climate\schange|global\swarming)\W+(?:\w+\W+){0,150}?(hoax|question|distant|(pseudoscientific|pseudoscience)|(socialism|socialist)|hysterical)\W+(?:\w+\W+){0,150}?(climate\schange|global\swarming)\b'
QUERY3_DESC = 'Denial-agentic framing'

def df_reduce():
    """Pull full database into dataframe"""
    crec_df = pd.read_sql("Select * from Reduced", CON, index_col='UTC')
    crec_df['html_data'] = crec_df['html_data'].str.replace('\n', ' ')
    crec_df = crec_df.set_index(pd.DatetimeIndex(crec_df.index)).loc[:'2021-12-27'] # (End Date?) Control date range of df
    return crec_df

def df_map():
    """Move database to pandas df, reduce by keyword, and map by regex counts."""
    query1_compiled = re.compile(QUERY1, re.IGNORECASE)
    query2_compiled = re.compile(QUERY2, re.IGNORECASE)
    query3_compiled = re.compile(QUERY3, re.IGNORECASE)

    query1_list = []
    query2_list = []
    query3_list = []

    for chunk in pd.read_sql("Select * from crec", CON, index_col='UTC',
                             chunksize=1000):
        chunk['html_data'] = chunk['html_data'].str.replace('\n', ' ')
        chunk = chunk.set_index(pd.DatetimeIndex(chunk.index)).loc[:'2021-12-27']
        chunk = chunk[chunk.html_data.str.contains(MAIN_KEYWORD)]

        query1_list.append(pd.DataFrame(index=chunk.index,
                                        data=chunk.html_data.str.count(query1_compiled)))
        query2_list.append(pd.DataFrame(index=chunk.index,
                                        data=chunk.html_data.str.count(query2_compiled)))
        query3_list.append(pd.DataFrame(index=chunk.index,
                                        data=chunk.html_data.str.count(query3_compiled)))

    query1_df = pd.concat(query1_list)
    query2_df = pd.concat(query2_list)
    query3_df = pd.concat(query3_list)

    return query1_df, query2_df, query3_df

def total_ratio():
    """Get ratio of all active-agentic:passive-agentic frames"""
    plot1_data, plot2_data, plot3_data = df_map()

    
    print(plot1_data.groupby(lambda x:x.year).sum())
    print(plot2_data.groupby(lambda x:x.year).sum())
    print(plot3_data.groupby(lambda x:x.year).sum())


def plot_frame():
    """Plot dataframes from regex_queries."""
    plot1_data, plot2_data, plot3_data = df_map()

    active_frame = []
    passive_frame = []
    denial_frame = []
    active_passive_frame = ([])
    active_denial_frame = ([])
    passive_denial_frame = ([])
    for i in plot1_data.groupby([lambda x: x.year,lambda x: x.quarter]).sum().iterrows():
        active_frame.append(i[1].values)
    for i in plot2_data.groupby([lambda x: x.year,lambda x: x.quarter]).sum().iterrows():
        passive_frame.append(i[1].values)
    for i in plot3_data.groupby([lambda x: x.year,lambda x: x.quarter]).sum().iterrows():
        passive_frame.append(i[1].values)

    print('Active: ' + str(type(active_frame)))
    print('Passive: ' + str(type(passive_frame)))
    print('Denial: ' + str(type(denial_frame)))
    for ac, pa in zip(active_frame, passive_frame):
        active_passive_frame.append(ac/pa)
    for ac, pa in zip(active_frame, passive_frame):
        active_denial_frame.append(ac/pa)
    for ac, pa in zip(active_frame, passive_frame):
        passive_denial_frame.append(ac/pa)
    round_active_passive_ratio = [round(float(elem),3) for elem in
            active_passive_frame]
    round_active_denial_ratio = [round(float(elem),3) for elem in
            active_denial_frame]
    round_passive_denial_ratio = [round(float(elem),3) for elem in
            passive_denial_frame]


    fig = plt.figure(figsize=(13,15))

    ax1 = plt.subplot(211)
    ax1.set_xlabel('Year', fontweight='bold')
    ax1.set_ylabel('Frequency', fontweight='bold')
    days = ["2016 Q1", "2016 Q2", "2016 Q3", "2016 Q4", "2017 Q1", "2017 Q2", "2017 Q3", "2017 Q4", "2018 Q1", "2018 Q2", "2018 Q3", "2018 Q4", "2019 Q1", "2019 Q2", "2019 Q3", "2019 Q4", "2020 Q1", "2020 Q2", "2020 Q3", "2020 Q4", "2021 Q1", "2021 Q2", "2021 Q3", "2021 Q4"]
    ax1.set_title('Agentic Frames in the Congressional Record', fontweight='bold', pad=15)
    plot1 = plt.bar(days,
                    plot1_data['html_data'].groupby([lambda x: x.year,lambda x: x.quarter]).sum(),
                    alpha=0.7, color="#FF5500", width=.2, align='edge')
    plot2 = plt.bar(days,
                    plot2_data['html_data'].groupby([lambda x: x.year,lambda x: x.quarter]).sum(),
                    alpha=0.5, color="#6495ED", width=.2)
    plot3 = plt.bar(days,
                    plot3_data['html_data'].groupby([lambda x: x.year,lambda x: x.quarter]).sum(),
                    alpha=0.5, color="#834173", width=.2, align='edge')
    plt.gcf().autofmt_xdate()
    plt.legend((plot1, plot2, plot3, (plot1, plot2, plot3)), (QUERY1_DESC, QUERY2_DESC, QUERY3_DESC), loc=2, fontsize=17)

    

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
    
    def autolabel_frames(rects):
        """
        Attach a text label above each bar displaying its height
        """
        for rect,item in zip(rects, round_active_passive_ratio):
            height = rect.get_height()
            ax1.text(rect.get_x() + rect.get_width()/2., 1.50+height,
                    item,
                    ha='center', va='bottom')
    #autolabel_frames(plot2)

    # Table Like: https://matplotlib.org/3.5.1/api/_as_gen/matplotlib.pyplot.table.html


    #For Each Quarter
    q_data = pd.DataFrame([
            days,
            active_frame, 
            passive_frame,
            denial_frame])

    #For Each Year
    y_data = pd.DataFrame([
            ['2016', '2017', '2018', '2019', '2020', '2021'],
            np.unique(plot1_data['html_data'].groupby([lambda x: x.year]).sum()), 
            np.unique(plot2_data['html_data'].groupby([lambda x: x.year]).sum()),
            np.unique(plot3_data['html_data'].groupby([lambda x: x.year]).sum())])


    q_data.to_excel('Quarters.xlsx')
    y_data.to_excel('Years.xlsx')

                          

    fig.savefig('fig.png')


df_reduce()
df_map()
total_ratio()
plot_frame()
