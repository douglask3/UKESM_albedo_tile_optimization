import iris
import numpy as np
from   libs.plot_temporals  import *
from   libs.ExtractLocation import *

regionNames = ['global', 'NA' , 'NA2', 'Asia', 'Asia2', 'Asia3']
east        = [ None   , 260.0, 275.0,  80.0 ,  80.0  , 80     ]
west        = [ None   , 310.0, 295.0, 105.0 , 105.0  , 105.0  ]
south       = [ None   ,  50.0,  45.0,  35.0 ,  45.0  , 30.0   ]
north       = [ None   ,  65.0,  55.0,  50.0 ,  55.0  , 40.0   ]

def plotRegion(dat, fign, regionName, jobID, levels, units = 'albedo', cmap = "pink", *args, **kw):
    dat = ExtractLocation(dat, *args, **kw).cubes
    figN = fign + '-' + regionName + '-'
    
    if len(dat.coord('time').points) > 12:
        plotInterAnnual(dat, jobID, figN, mnthLength = 1,
                        timeCollapse = iris.analysis.MEAN,
                        levels = levels, cmap = cmap, units = units)

    plotClimatology(dat, jobID, figN, mnthLength = 1,
                    timeCollapse = iris.analysis.MEAN, nyrNormalise = False,
                    levels = levels, cmap = cmap, units = units)

def plotAllRegions(dat, nm, *args, **kw):
    for r, e, w, s, n in zip(regionNames, east, west, south, north):
        plotRegion(dat, nm, r, east = e, west = w, south = s, north = n, *args, **kw)



