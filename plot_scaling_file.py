import iris
import numpy as np
from   os    import listdir, getcwd, mkdir, path, walk
from   pylab import sort
from   pdb   import set_trace as browser

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

data_dir = 'data/'
mod_out = 'ag589/'
stash_code = 'm01s00i289'

albedo_file = 'qrclim.land'
albedo_index = 0


## Load data
obs = iris.load(data_dir + albedo_file)[albedo_index]


def listdir_path(path):
    from os import listdir
    
    files = listdir(path)
    files = [path + i for i in files]
    return files

def define_axes():
    return plt.axes(projection=ccrs.Robinson())

mod_files = sort(listdir_path(data_dir + mod_out))
stash_contraint = iris.AttributeConstraint(STASH = stash_code)
mod = iris.load_cube(mod_files, stash_contraint)
browser()
## Seasonal tile

## Seaonal grid cell
mod_season = mod.collapsed('pseudo_level', iris.analysis.MEAN)

## Annual tile average
mod_tile = mod.collapsed('time', iris.analysis.MEAN)

## Annual grid cel avarage
def plot_aa(dat, plotN):
    plt.subplot(2, 1, plotN, projection=ccrs.Robinson())
    qplt.contourf(dat, 25, cmap = "brewer_Greys_09")
    plt.gca().coastlines()

    
obs_aa = obs.collapsed('time', iris.analysis.MEAN)
mod_aa = mod_tile[0,:,:]#.collapsed('pseudo_level', iris.analysis.SUM)

plot_aa(obs_aa, 1)
plot_aa(mod_aa, 2)

plt.show()

browser()
