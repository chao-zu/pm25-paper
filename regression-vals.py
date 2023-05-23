#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collocation data plot for sensor 1
Created on Tue Jun 28 14:09:35 2022

@author: jarl
"""

import pandas as pd
from pathlib import Path
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression

file = Path('/Users/jarl/Documents/Observatory/ccarph/Jeepney Data/Hourly Averages_new.xlsx')

# df = pd.read_excel(file, sheet_name='Time Series')\
#     .drop(columns=['Date', 'Time', 'Seconds']).dropna()

df = pd.read_excel(file, sheet_name='Time Series', usecols=['Sensor 1','Sensor 2', 'Sensor 3',
                                                            'Sensor 4', 'Sensor 5', 'Sensor 6',
                                                            'Sensor 7', 'BAM']).dropna()

# def stats2(sensor_col):
#     '''
#     Create linear regression

#     Parameters
#     ----------
#     sensor_col : str
#         DataFrame column label.

#     Returns
#     -------
#     Regression scores for the column.

#     '''
    
#     Y = df[sensor_col].values.reshape(-1, 1)
#     X = df['BAM'].values.reshape(-1, 1)
    
#     linear_regressor = LinearRegression()  # create object for the class
#     reg = linear_regressor.fit(X, Y)  # perform linear regression
    
#     print(f'\n*** {sensor_col} ***')
#     print(f'r2 = {round(reg.score(X,Y), 2)}')
#     print(f'slope = {round(reg.coef_[0][0], 2)}')
#     print(f'intercept = {round(reg.intercept_[0], 2)}')
    
#     return reg


def statsmodels(sensor_col):
    '''
    Get regression using statsmodels

    Parameters
    ----------
    sensor_col : str
        DataFrame column label.

    Returns
    -------
    reg : regression object
        reg.summary() shows the scores.

    '''
    
    Y = df[sensor_col].values
    X = df['BAM'].values
    X = sm.add_constant(X)
    
    res = sm.OLS(Y, X).fit()

    print(f'\n*** {sensor_col} ***')
    print(f"r2: {round(res.rsquared, 2)}")
    print(f'm, b: {round(res.params[1], 2)}, {round(res.params[0], 2)}')
    print(f"dm, db: {round(res.bse[1], 2)}, {round(res.bse[0], 2)}")
    
    return res
    

sensors = list(df.columns[:-1])

for sensor in sensors:
    # df[sensor] = df[sensor].apply(recalib)
    reg = statsmodels(sensor)
    