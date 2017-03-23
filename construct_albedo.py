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
from   libs.Albedo       import Albedo

from   libs.plot_maps    import *

###############################################
## Setup                                     ##
###############################################
Albe_file = 'data/qrclim.land'
Frac_file = 'data/N96e_GA7_17_tile_cci_reorder.anc'
LAI__file = 'data/N96e_GA7_qrparm.veg.13.pft.217.func.anc'
slAb_file = 'data/qrparm.soil'
slAb_varn = 'soil_albedo'

tile_lev = [101 ,102  ,103  ,201  ,202  ,3    ,301  ,302  ,4    ,401  ,402  ,501  ,502  ,6      , 7    , 8         , 9   ]
tile_nme = ['BD','TBE','tBE','NLD','NLE','C3G','C3C','C3P','C4G','C4C','C4P','SHD','SHE','Urban','Lake','Bare Soil','Ice']

alph_inf = [0.1 ,0.1  ,0.1  ,0.1  ,0.1  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.18   ,0.06  , -1.0       , 0.75]
alph_k   = [0.5 ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,None   ,None  ,None       ,None ]

minFracTests = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01]

albedoLevels = [0,  0.1, 0.2, 0.3, 0.4, 0.6, 0.8]
monthNames = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
              'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

###############################################
## Open data                                 ##
###############################################
frac    = iris.load_cube(Frac_file)
tileIndex = frac.coords('pseudo_level')[0].points
lais    = iris.load(LAI__file)
soilAlb = iris.load_cube(slAb_file, slAb_varn)

for i in range(0, 12):
    lais[i].add_aux_coord(iris.coords.DimCoord(np.int32(i),'time'))

lais = lais.merge()[0]
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
    plot_cubes_map(cube, nms, *args, **kw)


#plot_cubes_map_ordered(frac, 'brewer_Greens_09',
#                       [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5], 'max',
#                       'figs/N96e_GA7_17_tile_cci_reorder.png',
#                       'fractional cover')

#plot_cubes_map_ordered(mxLAI, 'brewer_Greens_09',
#                       [0, 1, 2, 3, 4, 5, 6, 7, 8], 'max',
#                       'figs/N96e_GA7_qrparm.veg.13.pft.217.func.annualMax.png',
#                       'LAI')

###############################################
## Pre-optimization plots                    ##
###############################################
def nTilesGT(frac, x, ai, ak):
    cube = frac.copy()
    np = 1 + float(ai is not None) + float(ak is not None)
    cube.data = (cube.data > x) * np
    return cube.collapsed('pseudo_level', iris.analysis.SUM)


ntiles = [nTilesGT(frac, i, None, None) for i in minFracTests]
#plot_cubes_map(ntiles, minFracTests, 'brewer_PuBuGn_09',
#               [0, 1, 2, 4, 6, 8], 'max',
#               'figs/nTilesGTx.png',
#               'no. tiles')

ntiles = [nTilesGT(frac, i, j, k) for (i, j, k) in zip(minFracTests, 
                                                    alph_infIndex, alph_kIndex)]
#plot_cubes_map(ntiles, minFracTests, 'brewer_RdPu_09',
#               [0, 3, 6, 9, 12], 'max',
#               'figs/nParamsGTx.png',
#               'no. Params')

###############################################
## Albedo construction                       ##
###############################################
albedo = Albedo(frac, lais, soilAlb,
                dict(zip(tile_lev, alph_inf)), dict(zip(tile_lev, alph_k)))


## annual cell albedo
cellAlbedo = albedo.cell(True)

###############################################
## Basic Albedo plots                        ##
###############################################
## tile albedo

plot_cubes_map_ordered(albedo.tiles(), 'pink',
               albedoLevels, 'max',
               'figs/constructed_tile_albedos.png',
               'albedo', figXscale = 4)

plot_cubes_map(albedo.cell(), monthNames, 'pink',
               albedoLevels, 'max',
               'figs/constructed_monthly_albedos.png',
               'albedo', figXscale = 4)

constructed = albedo.cell(True)

observed = iris.load(Albe_file)[0]
aobserved = observed.collapsed('time', iris.analysis.MEAN)
plot_cubes_map([constructed, aobserved], ['constructed', 'observed'], 'pink',
               albedoLevels, 'max',
               'figs/compare_albedos.png',
               'albedo', figXscale = 4)

browser()
