#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Count the time spent in TMEs.
Created on Mon Jun 13 13:07:05 2022

@author: jarl
"""

import pandas as pd
import numpy as np
from pathlib import Path
import xarray as xr

filename = Path('/Users/jarl/Documents/Observatory/ccarph/Jeepney Data/Alldata_tagged.csv')
df = pd.read_csv(filename, usecols=['Route.Number','calib_pm25', 'TME'], index_col=['Route.Number', 'TME']).rename(columns=dict(Longitude='lon', Latitude='lat'))

TMElist = ['UPTC', 'UP', 'Mcdo', 'Ateneo', 'Miriam', 'Terminal', 'Balara']
routeNumbers = list(df.index.get_level_values(0).unique())

def timeCount(routeNo):
    global TMElist
    routedf = df['calib_pm25'].loc[routeNo].sort_index()
    totaltime = {'UPTC':0, 'UP':0}
    
    for TME in TMElist:
        try:    # try-except is used cause no time is spent in the TME sometimes
            TMEtime = routedf.loc[TME].count()*15    # time spent at the tme in seconds (minutes=1/4), time spent = # of points * 15 seconds
            totaltime[TME] = TMEtime                 # add to dictionary

        except:
            totaltime[TME] = 0
        
    return totaltime
        

timedf = pd.DataFrame([timeCount(routeNo) for routeNo in routeNumbers])

timedf[timedf < 5000].boxplot(showfliers=False)
