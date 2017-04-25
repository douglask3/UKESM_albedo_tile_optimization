import libs.import_iris
import iris
import iris.coords
import numpy as np

import matplotlib.pyplot as plt
import cartopy.crs as ccrs


from   os                import listdir, getcwd, mkdir, path, walk
from   pylab             import sort
from   pdb               import set_trace as browser

from   libs              import git_info
from   libs.listdir_path import *
from   libs.weightedFuns import *
from   libs.which        import *
from   libs.nanRound     import *
from   libs.grid_area    import grid_area

from   libs.ExtractLocation import *
from   libs.Albedo          import Albedo
from   libs.plot_temporals  import *

from   libs.plot_maps     import *
from   libs.plotRegions   import *
from   libs.plotSWoverSW  import *

###############################################
## Setup                                     ##
###############################################
Albe_file = 'data/qrclim.land'
Frac_file = 'data/qrparm.veg.frac'
LAI__file = 'data/qrparm.veg.func'
LAI__varn = 'leaf_area_index'
slAb_file = 'data/qrparm.soil'
slAb_varn = 'soil_albedo'

tile_lev = [1   , 2   ,  3   ,  4   ,  5  ,  6     ,  7    , 8         , 9   ]
tile_nme = ['BL', 'NL', 'C3G', 'C4G', 'SH', 'Urban', 'Lake','Bare Soil','Ice']
alph_inf = [ 0.1,  0.1,  0.2 ,  0.2 , 0.2 ,  0.18  ,  0.06 , -1.0      , 0.75]
alph_k   = [ 0.5,  0.5,  0.5 ,  0.5 , 0.5 ,  None  ,  None , None      ,None ]

albedoLevels = [0,  0.1, 0.2, 0.3, 0.4, 0.6, 0.8]
monthNames = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
              'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

regionNames = ['global', 'NA' , 'NA2', 'Asia', 'Asia2']
east        = [ None   , 260.0, 275.0,  80.0 ,  80.0  ]
west        = [ None   , 310.0, 295.0, 105.0 , 105.0  ]
south       = [ None   ,  50.0,  45.0,  35.0 ,  45.0  ]
north       = [ None   ,  65.0,  55.0,  50.0 ,  55.0  ]


fign    = 'albedos_gc3.1'
ttle    = 'albedos'
unit    = 'albedo'

mod_dir_SW_  = 'u-ak518/SW/'

###############################################
## Open data                                 ##
###############################################
frac    = iris.load_cube(Frac_file)
tileIndex = frac.coords('pseudo_level')[0].points
lais    = iris.load_cube(LAI__file, LAI__varn)
soilAlb = iris.load_cube(slAb_file, slAb_varn)

mxLAI   = lais.collapsed('time', iris.analysis.MAX)
###############################################
## Indexing                                  ##
###############################################
tileIndex = frac.coords('pseudo_level')[0].points
PlotOrder = [which(tileIndex, i)[0] for i in tile_lev ]
ParaOrder = [which(tile_lev,  i)[0] for i in tileIndex]

def reOrder(lst, idx):  
    lst = [lst[i] for i in idx] 
    return lst

alph_infIndex = reOrder(alph_inf, ParaOrder)
alph_kIndex   = reOrder(alph_k  , ParaOrder)

###############################################
## Basic plotting                            ##
###############################################
def plot_cubes_map_ordered(cube, *args, **kw):
    codes = [frac.coords('pseudo_level')[0].points[i] for i in PlotOrder]
    cube = [cube[i] for i in PlotOrder if i < cube.shape[0]]
    nms = [i + '-' + str(j) for i,j in zip(tile_nme, codes)]
    plot_cubes_map(cube, nms, figXscale = 4, *args, **kw)


#plot_cubes_map_ordered(frac, 'brewer_Greens_09',
#                       [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5], 'max',
#                       'figs/GC3.1frac.png',
#                       'fractional cover')

#plot_cubes_map_ordered(mxLAI, 'brewer_Greens_09',
#                       [0, 1, 2, 3, 4, 5, 6, 7, 8], 'max',
#                       'figs/GC3.1MaxLAI.png',
#                       'LAI')

###############################################
## Albedo construction                       ##
###############################################
albedo = Albedo(frac, lais, soilAlb,
                dict(zip(tile_lev, alph_inf)), dict(zip(tile_lev, alph_k)))


## annual cell albedo
cell_sf_albedo  = albedo.cell()
###############################################
## Basic Albedo plots                        ##
###############################################
## tile albedo

plot_cubes_map_ordered(albedo.tiles(), 'pink',
               albedoLevels, 'max',
               'figs/constructed_tile_albedos.png',
               'albedo')#, figXscale = 4)

plot_cubes_map(cell_sf_albedo, monthNames, 'pink',
               albedoLevels, 'max',
               'figs/constructed_monthly_albedos.png',
               'albedo')#, figXscale = 4)


#def plotRegion(regionName, *args, **kw):
#    dat = ExtractLocation(cell_albedo, *args, **kw).cubes
#    figN = fign + '-' + regionName + '-'#

#    plotClimatology(dat, 'u-ak508', figN, mnthLength = 1,
#                    timeCollapse = iris.analysis.MEAN, nyrNormalise = False,
#                    levels = albedoLevels, units = '')

#for r, e, w, s, n in zip(regionNames, east, west, south, north):
#    plotRegion(r, east = e, west = w, south = s, north = n)


plotAllRegions(cell_sf_albedo, fign + 'snow_free', jobID = mod_dir_SW_[0:7], levels = albedoLevels)
plotSWoverSW(mod_dir_SW_, fign, jobID = mod_dir_SW_[0:7], levels = albedoLevels)


