#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate PUJ driver exposure using a simple model. Use maps_env.
Created on Mon May 30 11:00:55 2022

@author: jarl
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
from sklearn.linear_model import LinearRegression
import matplotlib.cm as cm
import statsmodels.api as sm

data = Path('/Users/jarl/Documents/Observatory/ccarph/Jeepney Data/Alldata_tagged.csv')

df = pd.read_csv(data, usecols=['datetime_fixed', 'calib_pm25', 'Route.Number',
                                'Longitude', 'Latitude', 'sensor'],
                 parse_dates=['datetime_fixed'], index_col=['Route.Number', 'datetime_fixed'])

df.drop(index=821, inplace=True)

routeNumbers = list(df.index.get_level_values(0).unique())

def totalDose(routeNo, rate=5.11E-3):
    '''
    Estimate the total dose (PM mass [µg]) deposited in the lungs assuming a 
    specific breathing rate.

    D = r int(C*dt) [m3/min]*[µg/m3]*[15s/(60s * 1 min)]

    Parameters
    ----------
    routeNo : int
        Select the route number over which to integrate.
    rate : num, optional
        Breathing rate. The default is sedentary (5.11E-3 m3/min).
        Optional: light (1.3E-2)

    Returns
    -------
    Tuple: total dose (µg) and total time elapsed (minutes)

    '''
    
    idf = df.loc[routeNo]
    idf.resample('15S').max().interpolate(inplace=True) 
    xpoints = idf.reset_index(drop=True).index.values*(15/60)
    minTotal = xpoints[-1]
    
    return(rate * np.trapz(idf['calib_pm25'], xpoints), minTotal, routeNo)


def doseRate(routeNo, rate=5.11E-3):
    idf = df.loc[routeNo]
    idf.resample('15S').max().interpolate(inplace=True) 
    xpoints = idf.reset_index(drop=True).index.values*(15/60)
    minTotal = xpoints[-1]
    
    return (rate * (np.trapz(idf['calib_pm25'], xpoints)/minTotal ), minTotal)


def stats(df, ax, use='sklearn'):
    
    global minTime
    X = df['Time'].values.reshape(-1,1) # values converts it into a numpy array
    Y = df.iloc[:, 0].values.reshape(-1,1) # -1 means that calculate the dimension of rows, but have 1 column ??? what did i mean by this
    
    if use=='sklearn':
        # linear regression: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
        
        linear_regressor = LinearRegression()  # create object for the class
        reg = linear_regressor.fit(X, Y)  # perform linear regression
        Y_pred = linear_regressor.predict(X)
        
        ax.plot(X, Y_pred, color='red', alpha=0.5)
        
        ax.text(0.05, 0.8, '$\mathrm{r^2 = }$' + f'{round(reg.score(X,Y), 2)}', 
                transform=ax.transAxes)
        ax.text(0.05, 0.72, f'{round(reg.coef_[0][0], 3)} $x + $ {round(reg.intercept_[0], 2)}',
                transform=ax.transAxes)
        
        return reg
        
    elif use == 'statsmodel':
        x = np.linspace(minTime, int(X.max()), int(X.max())*2)
        
        X = sm.add_constant(X)
        res = sm.OLS(Y, X).fit()
        pred_ols = res.get_prediction()
        # iv_l = pred_ols.summary_frame()["obs_ci_lower"]
        # iv_u = pred_ols.summary_frame()["obs_ci_upper"]
        
        m = round(res.params[1], 2)
        b = round(res.params[0], 2)
        r2 = round(res.rsquared, 2)
        
        ax.plot(x, (m*x + b), c='red', alpha=0.5)
        y1 = (res.conf_int()[1][0])*x + b
        y2 = (res.conf_int()[1][1])*x + b
        
        ax.fill_between(x, y1, y2, color='red', alpha=0.2)
        
        ax.text(0.05, 0.8, f'$r^2$ = {r2}', transform=ax.transAxes)
        ax.text(0.05, 0.72, f'y = {m}x + {b}', transform=ax.transAxes)
        
        return res
    else:
        pass
    
minTime = 18
dose1 = pd.DataFrame([totalDose(routeNo) for routeNo in routeNumbers], 
                    columns=['TotalDose','Time', 'RouteNumber'])
# dose = dose[dose['Time'] < 120]
dose = dose1[(dose1['Time'] < 120) & (dose1['Time'] > minTime)]

########## plotting ##########

# dose linear regression
fig, ax = plt.subplots(dpi=400, figsize=(4,3))
dose.plot(x=['Time'], y=['TotalDose'], ax=ax, kind='scatter', marker='.', 
          c='k', alpha=0.3)
ax.set_xlabel('Time (min)')
ax.set_ylabel('Inhaled dose (µg)')
est = stats(dose, ax, use='statsmodel')

# fig.savefig('/Users/jarl/Documents/Observatory/Figures/ccar/exposure.png',
#             bbox_inches='tight')

# dose rate
doserate = pd.DataFrame([doseRate(routeNo) for routeNo in routeNumbers], 
                    columns=['DoseRate','Time'])
doserate['Time'] = doserate['Time']/60
doserate['DoseRate'] = doserate['DoseRate']*60
doserate = doserate[(doserate['Time'] < 2) & (doserate['Time'] > 0.3)]

# plotting
histfig = plt.figure(dpi=300, figsize=(5,3))
gs = histfig.add_gridspec(1, 2, width_ratios=(4, 1), left=0.1, right=0.9, 
                          bottom=0.1, top=0.9, wspace=0.05)

ax1 = histfig.add_subplot(gs[1])
ax2 = histfig.add_subplot(gs[0], sharey=ax1)

doserate['DoseRate'].hist(bins=35, histtype='step',
                          grid=False, color='k', hatch='//', 
                          ax=ax1, orientation='horizontal',
                          density=True)

doserate.plot(x=['Time'], y=['DoseRate'], kind='scatter', marker='.',
              s=3, c='k', ax=ax2)

ax2.set_xlabel('Trip time (hr)')
ax2.set_ylabel('Dose rate (µg $\mathrm{hr^{-1}}$)')
ax2.set_xlim(0.25, 2.25)
ax2.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax2.xaxis.set_minor_locator(ticker.MultipleLocator(0.25))

median = doserate['DoseRate'].median()

ax1.axhline(median, c='r', linewidth=1)
ax2.axhline(median, c='r', linewidth=1)
ax2.text(2.05, median+1, f'{round(median,1)}', ha='center', color='red')

# histfig.savefig('/Users/jarl/Documents/Observatory/Figures/ccar/doserate.png',
#             bbox_inches='tight')

# run this to check stats
# dose['TotalDose'].describe()
# doserate['DoseRate'].describe()

# map diagnostics
weird_routes = dose1[(dose1['Time'] < minTime)].RouteNumber
for route in weird_routes:
    cmap = cm.rainbow # starts at purple, ends in red
    temp_fig, temp_ax = plt.subplots()
    temp_ax.scatter(df.loc[route].Longitude, df.loc[route].Latitude, c=df.loc[route].reset_index().index, cmap=cmap)
    triptime = str(dose1[dose1['RouteNumber']==route].Time)
    temp_ax.text(0.5, 0.5, triptime, ha='center', va='center', transform=temp_ax.transAxes)
    

