#############################################################################
## libs                                                                    ##
#############################################################################

import libs.import_iris #comment out this line if not run on CEH linux box
import iris
import numpy as np

from   libs                 import git_info
from   libs.load_stash      import *
from   libs.Albedo          import Albedo
from   libs.plotRegions     import *

from   pdb   import set_trace as browser  

#############################################################################
## cfg                                                                     ##
#############################################################################

## General
data_dir = 'data/'
mod_dir_veg  = 'u-ak518/u-ak518/'
mod_dir_SW_  = 'u-ak518/SW/'

## albedo
fign    = 'albedos_u-ak518'
ttle    = 'albedos'
unit    = 'albedo'

levels  = [0,  0.1, 0.2, 0.3, 0.4, 0.6, 0.8]
dlevels = np.array([0.01, 0.03, .1, .3])
dlevels = np.concatenate([-dlevels[::-1], dlevels])

cmap    = 'pink'

Frac_code = 'm01s19i013'
LAI__code = 'm01s19i014'
SWd__code = 'm01s01i210'
SWu__code = 'm01s01i211'

slAb_file = 'data/qrparm.soil'
slAb_varn = 'soil_albedo'

#############################################################################
## Params                                                                  ##
#############################################################################
tile_lev = [101 ,102  ,103  ,201  ,202  ,3    ,301  ,302  ,4    ,401  ,402  ,501  ,502  ,6      , 7    , 8         , 9   , 901, 902, 903, 904, 905, 906, 907, 908, 909, 910]
tile_nme = ['BD','TBE','tBE','NLD','NLE','C3G','C3C','C3P','C4G','C4C','C4P','SHD','SHE','Urban','Lake','Bare Soil','Ice','Ice1','Ice2','Ice3','Ice4','Ice5','Ice6','Ice7','Ice8','Ice9','Ice10']

alph_inf = [0.1 ,0.1  ,0.1  ,0.1  ,0.1  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.18   ,0.06  , -1.0       , 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75]
alph_k   = [0.5 ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,None   ,None  ,None       ,None,None,None,None,None,None,None,None,None,None,None ]


files   = sort(listdir_path(data_dir + mod_dir_veg))[0:120]
lais    = load_stash(files, LAI__code, 'lai' )
frac    = load_stash(files, Frac_code, 'frac')

soilAlb = iris.load_cube(slAb_file, slAb_varn)

sf_albedo = Albedo(frac, lais, soilAlb, dict(zip(tile_lev, alph_inf)),
                   dict(zip(tile_lev, alph_k)))
cell_sf_albedo  = sf_albedo.cell()

plotAllRegions(cell_sf_albedo, fign + 'snow_free', jobID = mod_dir_veg[0:7], levels = levels)

def plotSWoverSW(mod_dir, fign, *args, **kw):
    files   = sort(listdir_path(data_dir + mod_dir))[0:120]
    SWd     = load_stash(files, SWd__code, 'SWdown' )
    SWu     = load_stash(files, SWu__code, 'SWup')
    albedo  = SWu/SWd
    plotAllRegions(albedo, fign + 'all', *args, **kw)

plotSWoverSW(mod_dir_SW_, fign, jobID = mod_dir_veg[0:7], levels = levels)
