#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 30 14:32:25 2022

@author: xent
"""

import pandas as pd
import numpy as np
from pathlib import Path
import xarray as xr

filename = Path('/Users/jarl/Documents/Observatory/ccarph/Jeepney Data/Alldata_tagged.csv')
df = pd.read_csv(filename).rename(columns=dict(Longitude='lon', Latitude='lat'))

y0, x0 = 14.630245, 121.072649
y1, x1 = 14.633193, 121.075712
df['datetime_fixed'] = pd.to_datetime(df.datetime_fixed, format='%Y%m%d %H:%M:%S')
df['Datetime'] = df.datetime_fixed
rei = df.set_index(['sensor','Datetime'])
df.set_index('Datetime', inplace=True)

starts = df[((df.lon > x0) & (df.lon < x1)) & ((df.lat > y0) & (df.lat < y1))]
delta = (starts.datetime_fixed.values[1:] - starts.datetime_fixed.values[:-1])
starts['delta'] = starts.index - starts.index
starts.delta.iloc[:-1] = delta
starts['delta'] = starts.delta.dt.seconds
df['route'] = 0
df.loc[starts[starts.delta > 15*60].index, 'route'] = 1
# starts[starts.delta > 15*60]
starts['route'] = 0
starts.loc[starts.delta > 15*60, 'route'] = 1

df = df.reset_index()
df.set_index(['sensor','Datetime'], inplace=True)
df = df.loc[~df.index.duplicated()]
starts['routeno'] = starts['route'].cumsum()+1
# df.drop_duplicates(inplace=True)
df['routeno'] = df['route'].cumsum()+1