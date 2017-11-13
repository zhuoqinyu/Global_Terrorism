#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zhuoqinyu
"""
import pandas as pd
import numpy as np
import folium
import re
import json
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


#t_data=load_data()
#world_data=glob_data(t_data)


def load_json_file(filepath):
    '''
    Input:  Json file with country coordinates     | json
    OUtput: all the countries with their geo info  | dict
    ---
    NB: Using the with open method in json library
    returns a stabler output than using pandas' read json
    according to my practical experiement.
    '''
    # use regular expressions to check whether the input is a json file
    if not re.match(r'.+\.(json){1}$', filepath):
        raise LoadJsonError  # Error when not taking a json file as input
    else:
        with open('countries.geo.json') as json_data:
            j = json.load(json_data)
    return j

def find_js_country_names():
    '''
    load the geo json file
    get all the country names   |   numpy array
    '''
    j = load_json_file('countries.geo.json')
    ls = []
    for i in j['features']:
        ls.append(i['properties']['name'])
    return np.array(ls)

def js_country_names():
    '''
    Return all the names under the column "country"   |   DataFrame
    '''
    js_ctr = pd.DataFrame(find_js_country_names(), columns=['country'])
    return js_ctr

class choropleth_year_feature(object):
    '''
    feature can be casualties / death / injuries 
    '''
    def __init__(self,year,feature):
        self.year=year
        self.feature=feature
        self.byyear=glob_data(load_data()).set_index('year').loc[year].fillna(0)

        
    def feature_sum_ctr(self):
        df=self.byyear[['country',self.feature]]
        return df.groupby(['country']).sum()
    
    def max_feature(self):
        seri=self.feature_sum_ctr()[self.feature]
        return seri.max()
    
    def scale_max(self):
        '''
        Return the upper bound of the chosen feature for plotting
        '''
        return (int(self.max_feature()/100)+1)*100
    
    def sum_ctr_feature():
        self.feature_sum_ctr().reset_index()
        js_ctr=js_country_names()
        merge_df=pd.merge(feature_sum_ctr,js_ctr,on='country',how='outer').fillna(-99)
        df=merge_df.sort_values(by='country').reset_index().drop('index',1)
        return df

def choropleth_plot(color,feature,year):
    if int(year)==1993 or int(year) not in range(1970,2016):
        print("No available data")
    else:
        choropleth=choropleth_year_feature(year,feature)
        plot_data=choropleth.feature_sum_ctr().reset_index()
        world_geo= r'countries.geo.json'
        
        keys=[k['properties']["name"] for k in json.load(open(world_geo))['features']]
        missing_keys=set(keys)-set(plot_data['country'])
        dicts=[]
        for k in missing_keys:
            row={}
            dicts.append({'country':k,'Value':0})
        plot_data=plot_data.append(dicts,ignore_index=True)
        
        up=choropleth.scale_max()
        map = folium.Map(location=[45.523, -122.675],
                 zoom_start=2,
                 min_zoom=1,
                 tiles='Mapbox bright')
        map.choropleth(geo_path=world_geo, data=plot_data,
                       columns=['country', feature],
                       threshold_scale=[0, 500, up/3, up*2/3, up],
                       key_on='feature.properties.name',
                       fill_color=color, fill_opacity=0.7, line_opacity=0.2,
                       #legend_name='Scale',  # folium is not supportive to show legend_name on python 3.5
                       reset=True
                       )
        return map
def year_slider():
    '''
    Return a year from ipywidgets' IntSlider by users' manual pick
    '''
    yr = IntSlider(value=2010,
                   min=1970,
                   max=2015,
                   step=1,
                   description='Year',
                   disabled=False,
                   continuous_update=False,
                   orientation='horizontal',
                   readout=True,
                   readout_format='i',
                   slider_color='white'
                   )
    yr.layout.width = '80%'
    return yr


def color_palette_picker():
    '''
    Return a string of color indicator from users' manual pick
    '''
    return Dropdown(options={'Ocean': 'PuBu',
                             'Orchid': 'RdPu',
                             'NYU Pride': 'BuPu',
                             'Alert': 'OrRd',
                             'Grassland': 'GnBu',
                             'Orange':'YlOrRd'
                             },
                    value='YlOrRd',
                    description='Palette',
                    disabled=False,
                    button_style='info'
                    )
    
def feature_picker():
    '''
    Return a string of feature name from users' manual pick
    '''
    return ToggleButtons(options={'Deaths': 'death',
                                  'Wounds': 'injuries',
                                  'Casualties': 'casualties'
                                  },
                         value='casualties',
                         description='Feature',
                         disabled=False,
                         button_style='',  # 'success', 'info', 'warning', 'danger' or ''
                         tooltip='Description')

def Display_Your_Choropleth():
    '''
    Allow users to interactively explore data information
    and customize the choropleth map
    '''
    try:
        interact(choropleth_plot,
                 year=year_slider(),
                 feature=feature_picker(),
                 color=color_palette_picker())
    except: 
        print("No available data")
