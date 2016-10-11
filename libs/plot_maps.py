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
        if (len(lims) >= nlims0): return(lims)
    
    
    return(lims)


def plot_cube(cube, Ns, N, cmap):
    plt.subplot(Ns - 1, 2, N, projection=ccrs.Robinson())
    cube = cube.collapsed('time', iris.analysis.MEAN)
    
    cmap = plt.get_cmap(cmap)
    levels = hist_limits(cube, 7)
    
    norm = BoundaryNorm(levels, ncolors=cmap.N , clip=False)
    qplt.contourf(cube, levels = levels, cmap = cmap, norm = norm)
    plt.gca().coastlines()


def plot_cubes_map(cubes, *args):
    nplots = len(cubes)
    for i in range(0, nplots - 1): 
        print i 
        plot_cube(cubes[i], nplots, i * 2 + 1, *args)
    
    plot_cube(cubes[i + 1], nplots, 2, *args)


