#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 10:08:59 2022

@author: jarl
"""
import pandas as pd

file = '/Users/jarl/Documents/Observatory/ccarph/Jeepney Data/Alldata_tagged.csv'
# file = '/Users/jarl/Documents/Observatory/ccarph/Jeepney Data/Calibrated Data.csv'

df = pd.DataFrame(pd.read_csv(file, parse_dates=['datetime'], index_col=['datetime']))

#### if using calibrated data ####
# df = pd.DataFrame(pd.read_csv(file, usecols=['date', 'time', 'calib_pm25'], 
#                   parse_dates={'datetime':['date', 'time']}, index_col='datetime'))
# df['Day'] = ['Weekday' if x < 4 else 'Weekend' for x in df.index.dayofweek]

# weekday-weekend

wday = df.groupby('Day').get_group('Weekday')
wend = df.groupby('Day').get_group('Weekend')

## number of circuits
print('Number of ciruits (wday, wend):')
print(len(wday['Route.Number'].unique()))
print(len(wend['Route.Number'].unique()))
print('\n')

## pm2.5 mean
print('mean (wday, wend)')
print(wday['calib_pm25'].mean().round(1))
print(wend['calib_pm25'].mean().round(1))
print('\n')

## % above 90 mcg
print('% above 90 mcg (wend, wday)')
wend90 = wend['calib_pm25'].loc[wend['calib_pm25'] > 90].count()/wend['calib_pm25'].count()
print((wend90 * 100).round(2))

wday90 = wday['calib_pm25'].loc[wday['calib_pm25'] > 90].count()/wday['calib_pm25'].count()
print((wday90 * 100).round(2))
print('\n')


# rush hour

rushdf = df.groupby('Timegroup').get_group('peak')
amrush = rushdf.loc[(rushdf['Hour'] > 6) & (rushdf['Hour'] <= 12)]
pmrush = rushdf.loc[(rushdf['Hour'] > 12)]
nonrush = df.groupby('Timegroup').get_group('offpeak')

## mean
print('mean (am, non, pm)')
print(amrush['calib_pm25'].mean().round(1))
print(nonrush['calib_pm25'].mean().round(1))
print(pmrush['calib_pm25'].mean().round(1))
print('\n')

## % above 90 mcg
print('% above 90 mcg (am, non, pm):')
for d in [amrush, nonrush, pmrush]:
    df90 = d['calib_pm25'].loc[d['calib_pm25'] > 90].count()/d['calib_pm25'].count()
    print((df90 * 100).round(2))
print('\n')
    
## no of circuits
print('Number of circuits (am, non, pm):')
for d in [amrush, nonrush, pmrush]:
    print(len(d['Route.Number'].unique()))