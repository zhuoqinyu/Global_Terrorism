#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: zhuoqinyu
"""
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools
from plotly.offline import iplot, init_notebook_mode
init_notebook_mode()
import matplotlib.pyplot as plt
#%matplotlib inline
from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation
from IPython.display import HTML
import warnings
warnings.filterwarnings('ignore')
us_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY',
        'District of Columbia': 'DC'
    }
# Load data
def load_data():
    try:
        t_data = pd.read_csv('globalterrorismdb_0617dist.csv', encoding='ISO-8859-1')
        print('File load: Success')
    except:
        print('File load: Failed')
        
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

def glob_map_dens(data = None,level = None):
    plt.figure(figsize=(15,8))
    m = Basemap(projection='mill',llcrnrlat=-80,urcrnrlat=80, llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color='white',lake_color='lightblue', zorder = 1)
    m.drawmapboundary(fill_color='lightblue')
    def pltpoints_death(data=None,color = None, label = None):
        x, y = m(list(data.longitude[data.death > 0].astype("float")),\
            (list(data.latitude[data.death > 0].astype("float"))))
        points = m.plot(x, y, "o", markersize = 3, color = color, label = label, alpha = .5)
        return(points)
    
    def pltpoints_injuries(data =None,color = None, label = None):
        x, y = m(list(data.longitude[data.death == 0].astype("float")),\
            (list(data.latitude[data.death == 0].astype("float"))))
        points = m.plot(x, y, "o", markersize = 3, color = color, label = label, alpha = .5)
        return(points)
    def pltpoints_casualty(data =None,color = None, label = None):
        x, y = m(list(data.longitude[data.casualties!= 0].astype("float")),\
            (list(data.latitude[data.casualties != 0].astype("float"))))
        points = m.plot(x, y, "o", markersize = 3, color = color, label = label, alpha = .5)
        return(points)
    def pltpoints_occurrence(data =None,color = None, label = None):
        x, y = m(list(data.longitude.astype("float")),\
            (list(data.latitude.astype("float"))))
        points = m.plot(x, y, "o", markersize = 3, color = color, label = label, alpha = .5)
        return(points)
    if level=='injuries':
        pltpoints_injuries(data = data, color = "dodgerblue", label = "Injured")
        plt.title("Global Terrorism without Fatalities (1970 - 2015)")
        plt.legend(loc ='lower left', prop= {'size':11})
        plt.show()   
    elif level=='death':
        pltpoints_death(data = data, color = "red", label = "Fatal")
        plt.title("Global Terrorism with Fatalities (1970 - 2015)")
        plt.legend(loc ='lower left', prop= {'size':11})
        plt.show() 
    elif level=="casualties":
        pltpoints_casualty(data = data, color = "orange", label = "Casualties")
        plt.title("Global Terrorism Casualty Density (1970 - 2015)")
        plt.legend(loc ='lower left', prop= {'size':11})
        plt.show() 
    elif level=='occurrence':
        pltpoints_occurrence(data = data, color = "red")
        plt.title("Global Terrorism Occurrence Density (1970 - 2015)")
        #plt.legend(loc ='lower left', prop= {'size':11})
        plt.show()        
#Terrorism in the USA
def statepostal(row):
    return us_state_abbrev[row.state]

def data_usa(data=None):
    t_usa=data[(data.country == 'United States') and (data.state != 'Puerto Rico') and (data.longitude < 0)]
    states=list(set(t_usa["state"]))
    state_attack=[]
    def stateattack(row):
        for i, state in enumerate(states):
            if state == row.state:
                return state_attack[i]
    for state in states:
        state_attack.append(len(t_usa[t_usa.state == state]))
    t_usa['num_attack']=t_usa.apply(stateattack,axis=1)
    return t_usa
# Choropleth Maps

from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)
def choropleth_usa(t_usa):
    state_num=t_usa[["state","num_attack"]]
    state_num = state_num.drop_duplicates(["state","num_attack"])
    state_num['postal']=state_num.apply(statepostal,axis=1)
    scl = [[0.0, 'rgb(242,240,247)'],[0.2, 'rgb(218,218,235)'],[0.4, 'rgb(188,189,220)'],\
                [0.6, 'rgb(158,154,200)'],[0.8, 'rgb(117,107,177)'],[1.0, 'rgb(84,39,143)']]
    data=[dict(
            type='choropleth',
            colorscale = scl,
            autocolorscale = False,
            locations = state_num["postal"],
            locationmode="USA-states",
            z = state_num['num_attack'].astype(float),
            #text = df['text'],
            marker = dict(
                line = dict (
                    color = 'rgb(255,255,255)',
                    width = 2
                ) ),
            colorbar = dict(
                title = "Number of Attack")
            )]
    layout = dict(
            title = 'Terrorist Attacks in the USA (1970-2015)',
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                showlakes = True,
                lakecolor = 'rgb(255, 255, 255)'),
                 )
        
    fig = dict( data=data, layout=layout )
    iplot( fig, filename='d3-cloropleth-map' )