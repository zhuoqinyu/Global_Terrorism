#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zhuoqinyu
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
#from util import *

from ipywidgets import interact, ToggleButtons, Dropdown

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
worlddata=glob_data(load_data())
class gta(object):
    
    def __init__(self):
        self.df=worlddata
        self.region_names=worlddata.region.unique().tolist()
        self.attack_types=worlddata.attack.unique().tolist()
        self.target_types=worlddata.target.unique().tolist()
        self.us_states=worlddata[worlddata.country=='United States'].state.unique().tolist()
    
    def crt_in_region(self):
        crt_names={}
        for rg in self.region_names:
            crt_names[rg]=worlddata[worlddata.region==rg].dropna()['country'].unique().tolist()
        return crt_names
    
def heatmap_by_region(feature,region,cmap):
    df= gta().df[gta().df.region==region]
    df_cols=df[['year', 'country', feature]]
    df_cols.reset_index(inplace=True)
    hts=df_cols.groupby(['year','country']).sum()
    hts=hts.reset_index()
    
    fig=plt.figure(figsize=(25, int(len(gta().crt_in_region()[region])*3/4)))
    
    # use pivot table to set data in heatmap plot format
    pivot_table = hts.pivot('country', 'year', feature).fillna(0)
    plt.title('Annual {} in {} by Terror Attacks (1970-2015)\n'.format(feature.capitalize(),
                                                                               region), size = 20)
    plt.xlabel('Regions', size = 14)
    plt.ylabel('Years', size = 14)
    plt.xticks(rotation=-15)
    
    sns.heatmap(pivot_table,
                annot=False,
                fmt='.0f',
                linewidth=.5,
                square=True,
                cmap=cmap,
                cbar_kws={"orientation": "horizontal"})
    plt.show()
def heatmap_for_attack(feature,vs,cmap):
    df= gta().df
    df_cols=df[['attack', vs, feature]]
    df_cols.reset_index(inplace=True)
    hts=df_cols.groupby(['attack',vs]).sum()
    hts=hts.reset_index()
    
    fig=plt.figure(figsize=(25, int(len(gta().attack_types)*3/4)))
    
    # use pivot table to set data in heatmap plot format
    pivot_table = hts.pivot('attack',vs, feature).fillna(0)
    if vs=='year':
        plt.title('Annual {} Caused by Different Types of Terror Attacks (1970-2015)\n'.format(feature.capitalize()), size = 20)
        plt.ylabel('Years', size = 14)
    if vs=='region':
        plt.title('Regional {} Caused by Different Types of Terror Attacks (1970-2015)\n'.format(feature.capitalize()), size = 20)
        plt.ylabel('Region', size = 14)
    plt.xlabel('Attack', size = 14) 
    plt.xticks(rotation=-15)
    
    sns.heatmap(pivot_table,
                annot=False,
                fmt='.0f',
                linewidth=.5,
                square=True,
                cmap=cmap,
                cbar_kws={"orientation": "vertical"})
    plt.show()
def heatmap_for_target(feature,vs,cmap):
    df= gta().df
    df_cols=df[['target', vs, feature]]
    df_cols.reset_index(inplace=True)
    hts=df_cols.groupby(['target',vs]).sum()
    hts=hts.reset_index()
    
    fig=plt.figure(figsize=(25, int(len(gta().attack_types)*3/4)))
    
    # use pivot table to set data in heatmap plot format
    pivot_table = hts.pivot('target',vs, feature).fillna(0)
    if vs=='year':
        plt.title('Annual {} for Different Target Groups by Terror Attacks (1970-2015)\n'.format(feature.capitalize()), size = 20)
        plt.ylabel('Years', size = 14)
    if vs=='region':
        plt.title('Regional {} for Different Target Groups by Terror Attacks (1970-2015)\n'.format(feature.capitalize()), size = 20)
        plt.ylabel('Region', size = 14)
    plt.xlabel('Target Group', size = 14) 
    plt.xticks(rotation=-15)
    
    sns.heatmap(pivot_table,
                annot=False,
                fmt='.0f',
                linewidth=.5,
                square=True,
                cmap=cmap,
                cbar_kws={"orientation": "vertical"})
    plt.show()
def region_option():
    return Dropdown(options=gta().region_names,value='North America',
                    description='region',disabled=False,
                    button_style='info')
def feature_picker():
    return ToggleButtons(options={'Death': 'death',
                                  'Wound': 'injuries',
                                  'Casualty': 'casualties'
                                  },
                         value='casualties',
                         description='Feature',
                         disabled=False,
                         button_style='',
                         tooltip='Description')
def vs_picker():
    return ToggleButtons(options={'Year': 'year',
                                  'Region': 'region'
                                  },
                         value='year',
                         description='X-axis',
                         disabled=False,
                         button_style='',
                         tooltip='Description')
def Plot_heatmap_region():
    interact(heatmap_by_region,region=region_option(),feature=feature_picker(),cmap='Purples')
def Plot_heatmap_attack():
    interact(heatmap_for_attack,vs=vs_picker(),feature=feature_picker(),cmap='RdBu_r')
def Plot_heatmap_target():
    interact(heatmap_for_target,vs=vs_picker(),feature=feature_picker(),cmap='RdBu_r')