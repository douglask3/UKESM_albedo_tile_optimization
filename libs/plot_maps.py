import iris
import numpy as np
import cartopy.crs as ccrs

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from to_precision import *
from pdb import set_trace as browser

def hist_limits(dat, nlims, symmetrical = True):
    nlims0 = nlims
    for p in range(0,100 - nlims0):
        nlims = nlims0 + p
        
        lims = np.percentile(dat.data[~np.isnan(dat.data)], range(0, 100, 100/nlims))
        
        lims = [to_precision(i, 2) for i in lims]
        lims = np.unique(lims)
        if (len(lims) >= nlims0): break
   
    if (lims[0] < 0.0):        
        if (sum(lims <0.0) > sum(lims >0.0)):
            lims = lims[lims < 0.0]
            lims = np.concatenate((lims,-lims[::-1]))  
        else:
            lims = lims[lims > 0.0]
            lims = np.concatenate((-lims[::-1],lims))     
        extend = 'both'
    else:
        extend = 'max'
    return (lims, extend)


def plot_cube(cube, Ns, N, cmap):
    plt.subplot(Ns - 1, 2, N, projection=ccrs.Robinson())
    print cube.name()
    try:
        cube = cube.collapsed('time', iris.analysis.MEAN)
    except:
        cube = cube.collapsed('forecast_reference_time', iris.analysis.MEAN)
    
    cmap = plt.get_cmap(cmap)
    levels, extend = hist_limits(cube, 7)
    
    norm = BoundaryNorm(levels, ncolors=cmap.N + 1)
    #browser()
    qplt.contourf(cube, levels = levels, cmap = cmap, norm = norm, extend = extend)
    plt.gca().coastlines()


def plot_cubes_map(cubes, cmap, *args):
    nplots = len(cubes)
    for i in range(0, nplots - 1): 
        print i 
        
        if (type(cmap) is str):
            plot_cube(cubes[i], nplots, i * 2 + 1, cmap, *args)
        else: 
            plot_cube(cubes[i], nplots, i * 2 + 1, cmap[i], *args)
    
    if (type(cmap) is str):
        plot_cube(cubes[i + 1], nplots, 2, cmap, *args)
    else:        
        plot_cube(cubes[i + 1], nplots, 2, cmap[i+1], *args)


