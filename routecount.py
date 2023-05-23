#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figuring out how to split the routes better
Created on Mon May 30 14:30:14 2022

@author: jarl
"""
from pathlib import Path
import pandas as pd
import datetime as dt

x1, x2 = 121.072649, 121.075712
y1, y2 = 014.630245, 014.633193

### load data 
data = Path('/Users/jarl/Documents/Observatory/ccarph/Jeepney Data/Alldata_tagged.csv')

df = pd.read_csv(data, usecols=['datetime_fixed', 'calib_pm25', 'sensor', 'Latitude', 'Longitude',
                                'Route.Number'],
                 parse_dates=['datetime_fixed'], index_col=['sensor', 'datetime_fixed'])
df.sort_index(inplace=True)

def isInside(value, which):
    '''
    Is the data point inside the specified bounds?

    Parameters
    ----------
    value : coordinate
        Value to be verified.
    which : 'x' or 'y'
        Whether to check along x (lon) or y (lat).

    Returns
    -------
    bool
        True if inside the range.

    '''
    if which=='x':
        lo, hi = x1, x2
    else:
        lo, hi = y1, y2
        
    if lo <= value <= hi:
        return True
    else: return False
    
    
def pointcheck(lat, lon):
    '''
    Check if the point is inside the terminal

    Parameters
    ----------
    lat : latitude
        y-coordinate of the point.
    lon : longitude
        x-coordinate of the point.

    Returns
    -------
    bool
        Whether or not I'm in the terminal.

    '''
    routeProgress = False
    
    terminal = (isInside(lat, 'y') & isInside(lon,'x'))
    
    if terminal:
        routeProgress=True
        
    return(routeProgress)
    

def compare(before, current, time, date):
    '''
    Compare transitions in and out of the terminal. 
    current / before are states of whether I'm currently 
    in the terminal / whether I was previously in it.
    
    True -> False means I'm leaving the terminal
    False -> True means I'm arriving

    Parameters
    ----------
    before : bool
        Was I in the terminal in the previous time step?
    current : bool
        Am I in the terminal in this time step?
    time : time
        Current time.

    Returns
    -------
    routeno : int
        Routeno is either increased or left alone, depending on whether or not
        departCheck() is fulfilled.

    '''
    global routeno, terminaltime
    
    if before==True & current==False:
        # the PUJ is leaving the terminal
        
        if departCheck(time, date)==False:# did I leave less than 10 min ago?
            routeno += 1            # if this is a valid departure, increase routeno
            terminaltime[0] = time  # # if this is a valid departure, update the prev departure time
            terminaldate[0] = date
            return routeno          # update the total route number
        else:
            routeno += 0
            return routeno
        
    elif before==False & current==True:
        # the PUJ is arriving
        return routeno
    else:
        return routeno


def departCheck(current_time, date, mins=10):
    '''
    Check if I left the terminal less than 10 mins ago

    Parameters
    ----------
    current_time : time object
        Current time to be checked against terminaltime[0], the time I last 
        departed.

    Returns
    -------
    bool
        True if I left less than 10 mins ago: don't update route count.
        False if it's been more than 10 mins since I left'

    '''
    global terminaltime
    
    # date = dt.date(1, 1, 1)
    
    terminaltime[1] = current_time
    terminaldate[1] = date
    
    datetime1 = dt.datetime.combine(date, terminaltime[0])
    datetime2 = dt.datetime.combine(date, terminaltime[1])
    
    if datetime2 - datetime1 <= dt.timedelta(minutes=mins):
        print(datetime2- datetime1)
        return True
    else: return False


sensors_list = list(range(1,3)) # x,y up to but not including y

# add extra columns
df['InTerminal'] = df[['Latitude', 'Longitude']].apply(lambda row: pointcheck(row['Latitude'], row['Longitude']), axis=1)
df['PreInTerminal'] = df['InTerminal'].shift(1)
df['PreInTerminal'].fillna(False, inplace=True) # just to remove the nan part

routeno = 0
terminaltime = [dt.time(0,0), dt.time(0,0)] # previous depart, depart
terminaldate = [dt.date(1,1,1), dt.date(1,1,1)]

for sensor in sensors_list:
    sensordf = df.loc[sensor]
    terminaldate[0] = [sensordf.iloc[0].name.date()]
    terminaldate[1] = [sensordf.iloc[0].name.date()]
    sensordf['RouteCount'] = sensordf.apply(lambda x: 
                                            compare(x['PreInTerminal'], x['InTerminal'], 
                                                    x.name.time(), x.name.date()), axis=1)
