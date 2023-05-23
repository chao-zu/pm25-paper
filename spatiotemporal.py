"""
Spatiotemporal plots of PM2.5 in the UP-Katipunan PUJ route

@author: jarl
"""


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import geopandas as gpd
import cartopy.crs as ccrs
from shapely.geometry import Point
import contextily as ctx
import pyproj
import numpy as np
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from pathlib import Path

def add_basemap(gdf, ax, zoom, url='http://tile.stamen.com/terrain/tileZ/tileX/tileY.png'):
    """Add basemap to an Axes.

    This function adds a basemap from Stamen tiles. I think I just used a WGS84 extent to force the bounds here. 
    Different tile types are available on the website.

    Args:
        gdf (_type_): GeoDataFrame containing the points from which extents are computed
        ax (_type_): Figure Axes where the basemap is to be added
        zoom (_type_): Zoom level
        url (str, optional): URL for the basemap style Defaults to 'http://tile.stamen.com/terrain/tileZ/tileX/tileY.png'
    """
    # finding the extent of the input data so that the basemap covers the whole of the graph;
    # we use geopandas to convert the input dataframe to EPSG:3857 which is what contextily uses
    xmin, ymin, xmax, ymax = gdf.to_crs(epsg=3857).total_bounds 
    
    basemap, extent = ctx.bounds2img(xmin, ymin, xmax, ymax, zoom=zoom, url=url) 
    # bounds2img is a contextily function that takes the given basemap from stamen design
    
    #This is just a lambda function to reproject a given x & y coordinate from EPSG:3857 (which is the default contextily reference system) to EPSG:4326 
    #(which is WGS84, the usual default for QGIS; in case it doesn't work, you should try to see what EPSG file your input data is in).
#     reproject = lambda x, y: pyproj.transform(pyproj.Proj(init='EPSG:3857'),
#                                               pyproj.Proj(init='EPSG:4326'), x, y)

#     x1, y1 = reproject(extent[0], extent[2])
#     x2, y2 = reproject(extent[1], extent[3])
    wgs84_extent = 121.05877, 121.07879, 14.62918, 14.66153
    
    ax.imshow(np.flipud(basemap), extent=wgs84_extent, interpolation='bilinear')


def lat_lon_labels(ax, extent, nx = 2, ny = 3):
    """Create lat-lon labels.

    Args:
        ax (_type_): Axes where labels are appended
        extent (_type_): Axis bounds (unused)
        nx (int, optional): Number of ticks along x. Defaults to 2.
        ny (int, optional): Number of ticks along y. Defaults to 3.
    """
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top=False
    gl.ylabels_right=False
    gl.xlines =False
    gl.ylines = False
    gl.ylocator = mticker.MaxNLocator(ny)
    gl.xlocator = mticker.MaxNLocator(nx)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    

### gdf plotting ###
def spatiotemporal(gdf, axis):
    """Create spatiotemporal plot.

    Circles are placed centered at a pair of coordinates, 
    and colored by the cmap corresponding the the mean PM2.5 value.

    Args:
        gdf (_type_): GeoDataFrame from which spatiotemporal plot is created
        axis (_type_): Axes where plot is to be added
    """
    global extent, vmin, vmax, hide_label
    
    gdf.plot('calib_pm25', cmap='rainbow', ax=axis, vmin=vmin , vmax=vmax, 
             legend = False,edgecolors='k',linewidth=0.2, markersize=9, 
             legend_kwds={'label': 'PM Concentration ($\mu$g m$^{-3}$)', 'fraction':0.0785})

    add_basemap(gdf, axis, 16, 'http://tile.stamen.com/terrain/{z}/{x}/{y}.png')
    axis.set_extent(extent)
    if hide_label==False:
        lat_lon_labels(axis, extent)


### histogram plotting ###
def histplot(gdf, axis):
    """Create companion histogram for the spatiotemporal plot.

    Histograms are expressed as density, normalized by bin width (10 ug/m3), 
    controlled by the "density" argument.

    Args:
        gdf (_type_): GeoDataFrame from which spatiotemporal plot is created
        axis (_type_): Axes where plot is to be added
    """
    global hide_label
    n,bins,patches = axis.hist(gdf['calib_pm25'], density=True, 
                               bins=np.linspace(0,90,10), color='gray', 
                               linewidth=1, edgecolor='w')
    axis.set_xlim(0,90)
    axis.set_ylim(0, 0.05)
    axis.yaxis.set_major_locator(plt.LinearLocator(3))
    if hide_label == True:
        axis.set_yticklabels([])

    # cmhist = plt.cm.get_cmap('rainbow')
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    colr = bin_centers - min(bin_centers)
    colr /= max(colr)
    # for c, p in zip(colr, patches):
    #     plt.setp(p, 'facecolor', cmhist(c))


if __name__ == "__main__":
    ### Point these to the geojson files created using geopandas ###
    root = Path(input("Path to gdf data: "))
    alldata = [root/'Alldata_SpatiallyGrouped.geojson']

    rush = [root/'Filtered_AMPEAK_SpatiallyGrouped.geojson',
            root/'Filtered_OFFPEAK_SpatiallyGrouped.geojson',
            root/'Filtered_PMPEAK_SpatiallyGrouped.geojson'
            ]

    week = [root/'Filtered_Weekday_SpatiallyGrouped.geojson',
            root/'Filtered_Weekend_SpatiallyGrouped.geojson'
            ]

    # read the gdfs
    rush_gdf = []
    week_gdf = []

    alldata_gdf = gpd.read_file(alldata[0])

    for file in rush:
        gdf = gpd.read_file(file)
        rush_gdf.append(gdf)
        
    for file in week:
        gdf = gpd.read_file(file)
        week_gdf.append(gdf)

    extent = [121.05877, 121.07879, 14.62918, 14.66153]  # bounds of the plot (?)
    proj = ccrs.PlateCarree()  # set projection to be platecarree
    vmin, vmax = 0, 90  # limits of the colorbar/histogram


    ################ Rush hours ################
    fig = plt.figure(figsize=(7,5), dpi=250)
    gs = fig.add_gridspec(2,4, height_ratios=[4,1], width_ratios=[10,10,10,1])
    gs.update(hspace=0.2, wspace=0.1)

    # lists of subplots
    st = []
    hist = []

    # create subplots
    for i in range(3):
        spatemp = fig.add_subplot(gs[0, i], projection=proj)
        st.append(spatemp)
        histogram = fig.add_subplot(gs[1, i])
        hist.append(histogram)
        
    st[0].set_title('AM rush hours') 
    st[1].set_title('Non-rush hours') 
    st[2].set_title('PM rush hours') 
        
    # make spatiotemporal plots
    for i in range(3):
        hide_label = False  # hide labels to avoid redundancy
        if i>0:
            hide_label = True
        spatiotemporal(rush_gdf[i], st[i])
        histplot(rush_gdf[i], hist[i])
        
    # add colorbar shared by both plots
    cax = fig.add_subplot(gs[:,-1])
    sm = plt.cm.ScalarMappable(cmap='rainbow', norm=plt.Normalize(vmin=vmin, vmax=vmax))
    fig.colorbar(sm, cax=cax, extend='max')
    cax.set_ylabel('PM$_{2.5}$ Concentration ($\mu$g m$^{-3}$)')


    ################ Weekday-weekend ################
    fig2 = plt.figure(figsize=(5,5), dpi=250)
    gs2 = fig.add_gridspec(2,3, height_ratios=[4,1], width_ratios=[10,10,1])
    gs2.update(hspace=0.2, wspace=0.1)

    st2 = []
    hist2 = []

    for i in range(2):
        spatemp = fig2.add_subplot(gs2[0, i], projection=proj)
        st2.append(spatemp)
        histogram = fig2.add_subplot(gs2[1, i])
        hist2.append(histogram)

    st2[0].set_title('Weekday')
    st2[1].set_title('Weekend')

    for i in range(2):
        hide_label = False
        if i>0:
            hide_label = True
        spatiotemporal(week_gdf[i], st2[i])
        histplot(week_gdf[i], hist2[i])
        
    cax2 = fig2.add_subplot(gs2[:,2])
    fig.colorbar(sm, cax=cax2, extend='max')
    cax2.set_ylabel('PM$_{2.5}$ Concentration ($\mu$g m$^{-3}$)')


    ################ All runs/weekday/weekend ################
    fig3 = plt.figure(figsize=(7,5), dpi=250)
    gs3 = fig.add_gridspec(2,4, height_ratios=[4,1], width_ratios=[10,10,10,1])
    gs3.update(hspace=0.2, wspace=0.1)

    st3 = []
    hist3 = []

    for i in range(3):
        spatemp = fig3.add_subplot(gs3[0, i], projection=proj)
        st3.append(spatemp)
        histogram = fig3.add_subplot(gs3[1, i])
        hist3.append(histogram)

    hide_label = False
    spatiotemporal(alldata_gdf, st3[0])
    histplot(alldata_gdf, hist3[0])
        
    st3[0].set_title('All runs')
    st3[1].set_title('Weekday')
    st3[2].set_title('Weekend')

    for i in range(2):
        hide_label = True
        spatiotemporal(week_gdf[i], st3[i+1])
        histplot(week_gdf[i], hist3[i+1])
        
    cax3 = fig3.add_subplot(gs3[:,-1])
    fig3.colorbar(sm, cax=cax3, extend='max')
    cax3.set_ylabel('PM$_{2.5}$ Concentration ($\mu$g m$^{-3}$)')


    ################ Single plot for all data ################
    singlefig = plt.figure(figsize=(4,5), dpi=200)
    gs1 = gs.GridSpec(2, 2, height_ratios=[4,1], width_ratios=[10,1])

    st1 = plt.subplot(gs1[0, 0], projection=proj)
    st1.set_title('All runs')

    hist1 = plt.subplot(gs1[1, 0])

    hide_label = False

    spatiotemporal(alldata_gdf, st1)
    histplot(alldata_gdf, hist1)
        
    cax = plt.subplot(gs1[:,1])
    sm = plt.cm.ScalarMappable(cmap='rainbow', norm=plt.Normalize(vmin=vmin, vmax=vmax))
    singlefig.colorbar(sm, cax=cax, extend='max')
    cax.set_ylabel('PM$_{2.5}$ Concentration ($\mu$g m$^{-3}$)')
    singlefig.tight_layout()


    ### EDIT TO SAVE ###
    # fig.savefig(path + /rushhours.png, bbox_inches='tight', facecolor='w')
    # fig2.savefig(path + /week.png, bbox_inches='tight', facecolor='w')
    # fig3.savefig(path + /all_week.png, bbox_inches='tight', facecolor='w')
    # singlefig.savefig(path+'/allruns.png', bbox_inches='tight', facecolor='w')
