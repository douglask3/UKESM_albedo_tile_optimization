import libs.import_iris
import iris
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
from   libs.cellAlbedo   import cellAlbedo

from   libs.plot_maps    import *

Frac_file = 'data/N96e_GA7_17_tile_cci_reorder.anc'
LAI__file = 'data/N96e_GA7_qrparm.veg.13.pft.217.func.anc'

tile_lev = [101 ,102  ,103  ,201  ,202  ,3    ,301  ,302  ,4    ,401  ,402  ,501  ,502  ,6      , 7    , 8         , 9   ]
tile_nme = ['BD','TBE','tBE','NLD','NLE','C3G','C3C','C3P','C4G','C4C','C4P','SHD','SHE','Urban','Lake','Bare Soil','Ice']
alph_inf = [0.1 ,0.1  ,0.1  ,0.1  ,0.1  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.18   ,0.06  , 0.0       , 0.75]
alph_k   = [0.5 ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,None   ,None  ,None       ,None ]

minFracTests = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01]
def max_cubes(cubes):
    def tstMax(mx, nxt):
        msk = mx.data < nxt.data
        mx.data[msk] = nxt.data[msk]
        
        return mx
    
    mx = cubes[0]
    for i in cubes[1:]: mx = tstMax(mx, i)
    return mx



frac    = iris.load_cube(Frac_file)
lais    = iris.load(LAI__file)
mxLAI   = max_cubes(lais)

tileIndex = frac.coords('pseudo_level')[0].points
PlotOrder = [which(tileIndex, i)[0] for i in tile_lev ]
ParaOrder = [which(tile_lev,  i)[0] for i in tileIndex]

def reOrder(lst, idx):  
    lst = [lst[i] for i in idx] 
    return lst

alph_inf = reOrder(alph_inf, ParaOrder)
alph_k   = reOrder(alph_k  , ParaOrder)

#plot_cubes_map(frac, tile_nme, 'brewer_Greens_09',
#               [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5], 'max',
#               'figs/N96e_GA7_17_tile_cci_reorder.png',
#               'fractional cover')

#plot_cubes_map(mxLAI, tile_nme, 'brewer_Greens_09',
#               [0, 1, 2, 3, 4, 5, 6, 7, 8], 'max',
#               'figs/N96e_GA7_qrparm.veg.13.pft.217.func.annualMax.png',
#               'LAI')

def nTilesGT(frac, x, ai, ak):
    cube = frac.copy()
    np = 1 + float(ai is not None) + float(ak is not None)
    cube.data = (cube.data > x) * np
    return cube.collapsed('pseudo_level', iris.analysis.SUM)


ntiles = [nTilesGT(frac, i, None, None) for i in minFracTests]
plot_cubes_map(ntiles, minFracTests, 'brewer_PuBuGn_09',
               [0, 1, 2, 4, 6, 8], 'max',
               'figs/nTilesGTx.png',
               'no. tiles')

ntiles = [nTilesGT(frac, i, j, k) for (i, j, k) in zip(minFracTests, alph_inf, alph_k)]
plot_cubes_map(ntiles, minFracTests, 'brewer_RdPu_09',
               [0, 3, 6, 9, 12], 'max',
               'figs/nParamsGTx.png',
               'no. Params')

browser()
