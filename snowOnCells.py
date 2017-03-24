#############################################################################
## cfg                                                                     ##
#############################################################################
import numpy as np
## General
data_dir = 'data/'
mods_dir = ['u-ak508/', 'u-ak518/']
running_mean = False

## albedo
fign    = 'snowDays'
ttle    = 'Snow_Days'
unit    = 'days of snow on ground'

clim_levels  = np.arange(0, 35, 5)
clim_dlevels = np.array([0.1, 1, 3, 5, 10])
clim_dlevels = np.concatenate([-clim_dlevels[::-1], clim_dlevels])

ann_levels   = np.arange(0, 360, 30)
ann_dlevels  = np.array([1, 5, 10, 30, 90])
ann_dlevels  = np.concatenate([-ann_dlevels[::-1], ann_dlevels])

cmap    = 'brewer_GnBu_09'
dcmap   = 'brewer_Spectral_11'


#############################################################################
## libs                                                                    ##
#############################################################################

import libs.import_iris #comment out this line if not run on CEH linux box
import iris

from   pylab import sort      
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from   libs              import git_info
from   libs.plot_maps    import *
from   libs.plot_TS      import *
from   libs.listdir_path import *
from   libs.load_stash   import *

from   pdb   import set_trace as browser  

#############################################################################
## Funs                                                                    ##
#############################################################################
def loadCube(dir):
    files = sort(listdir_path(data_dir + dir))
    files = files[0:120]
    dat = iris.load_cube(files)
    dat.data = (dat.data > 0.00001) / 1.0
    return dat

def snowInJobMnth(dir, figN):    
    dat = loadCube(dir)
    
    mclim = dat[15::30].copy()

    for mn in range(0, mclim.shape[0]):
        md = mn * 30
        mclim.data[mn] = dat[md:(md+30)].collapsed('time', iris.analysis.SUM).data
    
    aclim = mclim[6::12].copy()

    for yr in range(0, aclim.shape[0]):
        ym = yr * 12
        aclim.data[yr] = mclim[ym:(ym+12)].collapsed('time', iris.analysis.SUM).data    
    
    labels = [str(i)[10:14] for i in aclim.coord('time')]
    return plotMapsTS(aclim, figN, dir, cmap, ann_levels, labels = labels), labels


def snowInJobClim(dir, figN):
    dat = loadCube(dir)

    dclim = dat[0:360].copy()
    mclim = dat[15:360:30].copy()

    ## convert to climatology
    nyrs = np.floor(dat.shape[0] / 360.0)

    for day in range(0, 360):
        dclim.data[day] = dat[day::360].collapsed('time', iris.analysis.SUM).data / nyrs

    for mn in range(0, 12):
        md = mn * 30
        mclim.data[mn] = dclim[md:(md+30)].collapsed('time', iris.analysis.SUM).data
    
    return plotMapsTS(mclim, figN, dir, cmap, clim_levels), 'JFMAMJJASOND'


def plotMapsTS(dat, figN, dir, cmap, levels, labels = 'JFMAMJJASOND',
              mdat = None, nx = 6, ny = 3, *args, **kw):
    if mdat is None: mdat = dat

    try: dat.units = 'days'
    except: pass

    plot_cubes_map(mdat, labels, cmap, levels, nx = 6, ny = 3,
                   cbar_yoff = 0.25, projection = None, *args, **kw)
    
    plt.subplot(4, 1, 4)
    
    tdat = dat if type(dat) == list else [dat]
    plot_cube_TS(tdat, False, ylabel = unit)
    
    plt.title(dir[:-1])  
    
    fig_name = 'figs/' + fign + '-' + figN + '-' + dir[:-1] + '.png'
    plt.savefig(fig_name)

    try: dat.var_name = dat.long_name = dir[:-1]
    except: pass
    return dat


def snowInJobs(FUN, levels, figN):
    
    snowDays = [FUN(dir, figN) for dir in mods_dir]
    labels = snowDays[0][1]
    snowDays = [i[0] for i in snowDays]

    diff = snowDays[0].copy()
    diff.data = snowDays[1].data - snowDays[0].data
    
    title = mods_dir[1][:-1] + '-' + mods_dir[0][:-1] + '/'
    plotMapsTS(snowDays, figN, title, dcmap, levels, labels, diff, extend = 'both')


snowInJobs(snowInJobMnth,  ann_dlevels, 'annual')
snowInJobs(snowInJobClim, clim_dlevels, 'climty')

