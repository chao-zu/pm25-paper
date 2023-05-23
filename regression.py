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

df = pd.read_excel(file, sheet_name='Time Series', usecols=['Sensor 1','Sensor 2', 'Sensor 3',
                                                            'Sensor 4', 'Sensor 5', 'Sensor 6',
                                                            'Sensor 7', 'BAM']).dropna()
df = df.dropna()

# df['datetime']= pd.to_datetime(df['Seconds'], unit='s')
# df.set_index('Sensor 1', inplace=True)

def recalib(pm25, m=1.169, b=0):
    return pm25 / m + b
    
# df['Sensor 1'] = df['Sensor 1'].apply(recalib)

def stats(df, ax):
    
    Y = df['Sensor 1'].values
    X = df['BAM'].values
    X = sm.add_constant(X)
    
    res = sm.OLS(Y, X).fit()
    
    pred_ols = res.get_prediction()
    
    m = round(res.params[1], 2)
    b = round(res.params[0], 2)
    r2 = round(res.rsquared, 2)
    
    x = np.linspace(0, 50, 100)
    y = m*x + b
    
    ax.plot(x, y, ls=':', c='k', label='regression line')

    ax.text(0.5, 0.42, f'$r^2$ = {r2}', transform=ax.transAxes)
    ax.text(0.5, 0.37, f'y = {m}x + {b}', transform=ax.transAxes)
    
    return res

# def stats2(df, ax):
    
#     Y = df['Sensor 1'].values.reshape(-1, 1)
#     X = df['BAM'].values.reshape(-1, 1)
    
#     linear_regressor = LinearRegression()  # create object for the class
#     reg = linear_regressor.fit(X, Y)  # perform linear regression
#     Y_pred = linear_regressor.predict(X)
    
#     ax.plot(X, Y_pred, color='k', ls=':', label='regression line')
    
#     ax.text(0.05, 0.7, '$\mathrm{r^2 = }$' + f'{round(reg.score(X,Y), 2)}', 
#             transform=ax.transAxes)
#     ax.text(0.05, 0.62, f'{round(reg.coef_[0][0], 2)} $x + $ ({round(reg.intercept_[0], 2)})',
#             transform=ax.transAxes)


fig, ax = plt.subplots(figsize=(4,4), dpi=200)
df.plot.scatter(x='BAM', y='Sensor 1', ax=ax, c='red', label='AS-LUNG S1')
ax.plot(np.linspace(0,60,101), np.linspace(0,60,101), c='blue', label='1:1 line')

res = stats(df, ax)

ax.set_ylabel('AS-LUNG S1 $\mathrm{PM_{2.5}}$ concentrations (µg $\mathrm{m^{-3}}$)')
ax.set_xlabel('BAM $\mathrm{PM_{2.5}}$ concentrations (µg $\mathrm{m^{-3}}$)')

ax.legend(fontsize='small', loc='lower right')

ax.set_aspect('equal')
ax.set_xlim(0,50)
ax.set_ylim(0,50)

fig.savefig('/Users/jarl/Documents/Observatory/Figures/ccar/regression_switch.png', bbox_inches='tight')
