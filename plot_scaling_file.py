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

albedo_file = 'qrclim.land'
albedo_index = 0


## Load data
obs = iris.load(data_dir + albedo_file)[albedo_index]

def define_axes():
    return plt.axes(projection=ccrs.Robinson())


## Annual tile average
aa = obs.collapsed('time', iris.analysis.MEAN)

## Annual grid cel avarage
def plot_map(dat, plotN):
    plt.subplot(2, 1, plotN, projection=ccrs.Robinson())
    qplt.contourf(dat, 25, cmap = "brewer_Greys_09")
    plt.gca().coastlines()


plot_map(aa, 1)
## add seasonal plots

plt.show()

browser()
