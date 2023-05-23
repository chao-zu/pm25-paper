# -*- coding: utf-8 -*-
"""
Analysing wind data for the sampling period
Created on Mon May 30 14:30:14 2022

@author: jarl
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

file = Path('/Users/jarl/Documents/Observatory/Data/ccar/MOIP_201811-201812.csv')
df = pd.read_csv(file, usecols=['Datetime','WindSpeed', 'u', 'v'], 
                 na_values='-999', parse_dates=['Datetime'], 
                 index_col='Datetime')

df.dropna(inplace=True)

# df = df.loc['2018-Nov-12':'2018-Dec-15']

uv_abs = np.sqrt(df['u']**2 + df['u']**2)

fig, ax = plt.subplots(figsize=(12,3))
q = ax.quiver(df['u'], df['v'], df['WindSpeed'], pivot='mid', scale=50, headwidth=2)
ax.set_yticklabels([])
ax.set_yticks([])
cb = plt.colorbar(q, pad=0.01)

date_grouped = df.groupby(df.index.date)

fig1, ax1 = plt.subplots()
for i, date in enumerate(pd.date_range('2018-Nov-12', '2018-Dec-15')):
    try:
        daydf = date_grouped.get_group(date)
        ax1.quiver([daydf.index.hour, i], df['u'], df['v'], df['WindSpeed'])
    except:
        pass
    