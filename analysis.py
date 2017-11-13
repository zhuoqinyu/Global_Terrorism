#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zhuoqinyu
"""

import pandas as pd
import numpy as np
import matplotlib. pyplot as plt
import seaborn as sns
import sys
import ini_data
import scipy 
from ipywidgets import widgets, IntSlider, Dropdown, interact, ToggleButtons

# Load data
def load_data():

    t_data = pd.read_csv('globalterrorismdb_0617dist.csv', encoding='ISO-8859-1')
        
    t_data = t_data.rename(
        columns={'eventid':'id', 'iyear':'year', 'imonth':'month', 'iday':'day', 'provstate':'state','attacktype1_txt':'attack', 'targtype1_txt':'target',
                 'weaptype1_txt':'weapon', 'nkill':'death', 'nwound':'injuries','country':'country_id','country_txt':'country','region':'region_id','region_txt':'region'})
    return t_data
# Global analysis
def glob_data(t_data):
    t_data['death']=t_data['death'].fillna(0).astype(int)
    t_data['injuries']=t_data['injuries'].fillna(0).astype(int)
    t_gob=t_data[['id', 'day','month','year', 'state', 'latitude', 'longitude','attack','target', 'weapon', 'death', 'injuries',"country","region"]]
    t_gob['day']=t_gob['day'].astype(int)
    t_gob['month']=t_gob['month'].astype(int)
    t_gob['day'][t_gob.day==0]=1
    t_gob['month'][t_gob.month==0]=1
    t_gob['casualties']=t_gob['death']+t_gob['injuries']
#    t_gob['date']=pd.to_datetime(t_gob[['day', 'month', 'year']])
#    t_gob = t_gob.sort_values(['death', 'injuries'], ascending = False)
#    t_gob = t_gob.drop_duplicates(['date', 'latitude', 'longitude', 'death'])
    return t_gob

world_data=glob_data(load_data())

def valid_country_names():
    df=glob_data(load_data())
    all_ctr = sorted(df.country.unique())
    all_ctr.insert(0, 'World')
    return all_ctr

def df_occur_country_nonzero_year(country): #return a dataframe for a country containing occurences each year
    if country=="World":
        df_c=world_data
    else:
        df_c=world_data.set_index('country').ix[country]
        if type(df_c)==pd.Series:
            df_c=pd.DataFrame(df_c).T
    df_yr=pd.DataFrame(df_c.groupby('year').count().id)
    df_yr.columns=['occurrences']
    return df_yr.reset_index()

def df_occur_country_all_year(country):

    dic_years={'year':list(range(1970,2016)),'null': np.zeros((2015-1970)+1, dtype=int)}
    df_years=pd.DataFrame(dic_years)
    df_full_yr=pd.merge(df_years,df_occur_country_nonzero_year(country),on='year',how='outer').fillna(0)
    return df_full_yr[['year','occurrences']]

def df_ctr_all(country):
    if country=="World":
        df1=world_data
    else:
        df1 = world_data[world_data.country==country]
    df1=df1.groupby('year').sum().reset_index()
    df2 = df_occur_country_all_year(country)
    df_merge = pd.merge(df1, df2, on='year', how='outer').fillna(0).sort_values(by='year')
    df = df_merge.reset_index().drop(['index'], 1)
    return df[df.year!=1993] 

def country_stats(country):
    df1=df_ctr_all(country)
    stats=df1[['death','injuries','casualties','occurrences']].describe().T
    stats['sum']=df_ctr_all(country).sum()
    return stats

def analy_country(country):

    desc = country_stats(country)
    df_ixby_yr = df_ctr_all(country).set_index('year')
#    df_ixby_yr['casualties']=df_ixby_yr['death']+df_ixby_yr['injuries']
    analysis_str = '\
                              Statistical Analysis Report ( {} )                      \n\
--------------------------------------------------------------------------------------------------\n\
                From 1970 to 2015:                                               \n\
                - The year with the most attacks:        {}                                 \n\
                         * {} times of terror attacks in {} in this year                    \n\
                - The year with the most casulties:      {}                                 \n\
                         * {} people were killed or wounded.                                \n\
                         * {} times of terror attacks in {} in this year                    \n\
                - Occurrences of Terrorism Attacks                                          \n\
                         * The total number:             {} \n \
                        * The annual average:            {} \n \
                        * The standard deviation:        {} \n \
               - Casualties                                 \n \
                    1) The total number:                 {} \n \
                        * death                          {} \n \
                        * injuries                       {} \n \
                    2) The annual average:               {} \n \
                        * death                          {} \n \
                        * injuries                       {} \n \
                    3) The standard deviation:           {} \n \
                        * death                          {} \n \
                        * injuries                       {} \n \
--------------------------------------------------------------------------------------------------\n '

    analysis = analysis_str.format(country,
                                   np.argmax(df_ixby_yr.occurrences),               # the year with maximum occurrence
                                   int(df_ixby_yr.occurrences.max()),               # the maximum occurrence
                                   country,
                                   np.argmax(df_ixby_yr.casualties),          # the year with maximum casualties
                                   str(int(desc.loc['casualties', 'max'])),   # the largest number of casualties
                                   str(int(desc.loc['occurrences', 'max'])),        # the largest number of occurrences
                                   country,
                                   str(int(desc.loc['occurrences', 'sum'])),        # total number of attacks
                                   str(int(desc.loc['occurrences', 'mean'])),       # mean of annual attacks
                                   str(desc.loc['occurrences', 'std']),             # std of annual attacks
                                   str(int(desc.loc['casualties', 'sum'])),   # total number of casualties
                                   str(int(desc.loc['death', 'sum'])),        # total number of people killed
                                   str(int(desc.loc['injuries', 'sum'])),       # total number of wounded
                                   str(int(desc.loc['casualties', 'mean'])),  # mean of annual casualties
                                   str(int(desc.loc['death', 'mean'])),       # mean of annual kills
                                   str(int(desc.loc['injuries', 'mean'])),      # mean of annual wounds
                                   str(desc.loc['casualties', 'std']),        # std of annual casualties
                                   str(desc.loc['death', 'std']),             # std of annual kills
                                   str(desc.loc['injuries', 'std']),            # std of annual wounds
                                  )
    return analysis

def report_time_series(country,feature): # feature is a list\

    color_dic={"death":"red","injuries":"orange","casualties":"purple","occurrences":"green"}
    if country not in valid_country_names():
        print("No such country in database")
    else:
        fig=plt.figure(figsize=(15,5))
        df=df_ctr_all(country)   
        x=df.year
        x=np.array(x)
        x_smooth=np.linspace(x.min(),x.max(),500)
        sns.set(style='whitegrid')

        for ft in feature:  
            mean=country_stats(country)['mean'].loc[ft]
            y=df[ft]
            y=np.array(y)
            y_smooth=scipy.interpolate.spline(x,y,x_smooth)
            plt.plot(x_smooth,y_smooth,'-',color=color_dic[ft],linewidth=3,label='{} in {}'.format(ft.capitalize(), country))
            plt.axhline(y=mean, label='Average {}'.format(ft.capitalize()),
                    color=color_dic[ft], linewidth=1, linestyle='dashed')
        plt.ylim(ymin=0)
        plt.title('Terrorist Attack ( {} ) (1970-2015)'.format(country),size=15)
        plt.xlabel('Year',size=14)
        plt.ylabel('Count',size=14)
        plt.legend()
        plt.show()
        print(analy_country(country))
        
def country_picker():
    '''
    Return a string of country name from users' manual pick
    '''
    return Dropdown(options=valid_country_names(),
                    value='World',
                    description='Country:',
                    disabled=False,
                    button_style='info'
                    )

def feature4_picker():
    '''
    Return a string of feature name from users' manual pick
    '''
    return Dropdown(options={'Occurrence': ['occurrences'],
                             'Casualty': ['casualties'],
                             'Death': ['death'],
                             'Wound': ['injuries'],
                             'All':["death","injuries","occurrences","casualties"]},
                    value=['occurrences'],
                    description='Feature:',
                    disabled=False,
                    button_style='info'
                    )
    
def Display_report_time_series():
    '''
    Allow users to interactively explore data information
    and customize:
        - the lineplot
        - the Statistical Analysis
    '''
    try:
        interact(report_time_series,
                 country=country_picker(),
                 feature=feature4_picker())
    except:
        print('No data')