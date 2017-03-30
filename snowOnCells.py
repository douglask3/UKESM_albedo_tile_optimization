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

ann_levels   = np.arange(0, 390, 30)
ann_dlevels  = np.array([1, 5, 10, 30, 90])
ann_dlevels  = np.concatenate([-ann_dlevels[::-1], ann_dlevels])

cmap    = 'brewer_GnBu_09'
dcmap   = 'brewer_Spectral_11'

regionNames = ['global', 'NA' , 'NA2', 'Asia', 'Asia2']
east        = [ None   , 260.0, 275.0,  80.0 ,  80.0  ]
west        = [ None   , 310.0, 295.0, 105.0 , 105.0  ]
south       = [ None   ,  50.0,  45.0,  35.0 ,  45.0  ]
north       = [ None   ,  65.0,  55.0,  50.0 ,  55.0  ]

   

#############################################################################
## libs                                                                    ##
#############################################################################

import libs.import_iris #comment out this line if not run on CEH linux box
import iris
       
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from   libs              import git_info
from   libs.plot_maps    import *
from   libs.plot_TS      import *
from   libs.load_stash   import *
from   libs.ExtractLocation import *

from   pdb   import set_trace as browser  

#############################################################################
## Funs                                                                    ##
#############################################################################
def snowInJobMnth(dir, figN, *args, **kw):    
    dat = loadCube(dir, *args, **kw)
    
    mclim = dat[15::30].copy()

    for mn in range(0, mclim.shape[0]):
        md = mn * 30
        mclim.data[mn] = dat[md:(md+30)].collapsed('time', iris.analysis.SUM).data
    
    aclim = mclim[6::12].copy()

    for yr in range(0, aclim.shape[0]):
        ym = yr * 12
        aclim.data[yr] = mclim[ym:(ym+12)].collapsed('time', iris.analysis.SUM).data    
    
    labels = [str(i)[10:14] for i in aclim.coord('time')]
    mclim = plotMapsTS(mclim, figN, dir, cmap, ann_levels, labels = labels, mdat = aclim)
    return mclim, aclim, labels


def snowInJobClim(dir, figN, *args, **kw):
    dat = loadCube(dir, *args, **kw)

    dclim = dat[0:360].copy()
    mclim = dat[15:360:30].copy()

    ## convert to climatology
    nyrs = np.floor(dat.shape[0] / 360.0)

    for day in range(0, 360):
        dclim.data[day] = dat[day::360].collapsed('time', iris.analysis.SUM).data / nyrs

    for mn in range(0, 12):
        md = mn * 30
        mclim.data[mn] = dclim[md:(md+30)].collapsed('time', iris.analysis.SUM).data
    mclim = plotMapsTS(mclim, figN, dir, cmap, clim_levels)
    return mclim, mclim, 'JFMAMJJASOND'


def plotMapsTS(dat, figN, dir, cmap, levels, labels = 'JFMAMJJASOND',
              mdat = None, nx = 6, ny = 3, running_mean = False, *args, **kw):
    if mdat is None: mdat = dat

    try: dat.units = 'days'
    except: pass

    plot_cubes_map(mdat, labels, cmap, levels, nx = 6, ny = 3,
                   cbar_yoff = 0.25, projection = None, *args, **kw)
    
    plt.subplot(4, 1, 4)
    
    tdat = dat if type(dat) == list else [dat]
    plot_cube_TS(tdat, running_mean, ylabel = unit)
    
    plt.title(dir[:-1])  
    
    fig_name = 'figs/' + fign + '-' + figN + '-' + dir[:-1] + '.png'
    plt.savefig(fig_name)

    try: dat.var_name = dat.long_name = dir[:-1]
    except: pass
    return dat


def snowInJobs(FUN, levels, regionName, figN, running_mean = False, *args, **kw):
    
    figN = figN + '-' + regionName
    snowDays = [FUN(dir, figN, *args, **kw) for dir in mods_dir]
    
    labels = snowDays[0][2]
    #snowDays = [i[0] for i in snowDays]

    diff = snowDays[1][1].copy()
    diff.data -= snowDays[0][1].data
    tdat = [snowDays[0][0], snowDays[1][0]]
    
    title = mods_dir[1][:-1] + '-' + mods_dir[0][:-1] + '/'
    plotMapsTS(tdat, figN, title, dcmap, levels, labels,
               diff, running_mean = running_mean, extend = 'both')


def plotRegion(regionName, *args, **kw):
    snowInJobs(snowInJobMnth,  ann_dlevels, regionName,  'annual', True, *args, **kw)
    snowInJobs(snowInJobClim, clim_dlevels, regionName, 'climty', *args, **kw)

for r, e, w, s, n in zip(regionNames, east, west, south, north):
    plotRegion(r, east = e, west = w, south = s, north = n)
