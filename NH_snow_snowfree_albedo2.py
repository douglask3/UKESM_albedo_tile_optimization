#############################################################################
## cfg                                                                     ##
#############################################################################
import numpy as np
## General
data_dir = 'data/'
mod_dir  = 'u-ak518/u-ak518/'

## albedo
fign    = 'albedos_u-ak518'
ttle    = 'albedos'
unit    = 'albedo'

clim_levels  = [0,  0.1, 0.2, 0.3, 0.4, 0.6, 0.8]
clim_dlevels = np.array([0.01, 0.03, .1, .3])
clim_dlevels = np.concatenate([-clim_dlevels[::-1], clim_dlevels])

ann_levels   = clim_levels
ann_dlevels  = clim_dlevels

cmap    = 'pink'
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
from   libs.Albedo       import Albedo

from   pdb   import set_trace as browser  

#############################################################################
## Funs                                                                    ##
#############################################################################

Frac_code = 'm01s19i013'
LAI__code = 'm01s19i014'


slAb_file = 'data/qrparm.soil'
slAb_varn = 'soil_albedo'

tile_lev = [101 ,102  ,103  ,201  ,202  ,3    ,301  ,302  ,4    ,401  ,402  ,501  ,502  ,6      , 7    , 8         , 9   , 901, 902, 903, 904, 905, 906, 907, 908, 909, 910]
tile_nme = ['BD','TBE','tBE','NLD','NLE','C3G','C3C','C3P','C4G','C4C','C4P','SHD','SHE','Urban','Lake','Bare Soil','Ice','Ice1','Ice2','Ice3','Ice4','Ice5','Ice6','Ice7','Ice8','Ice9','Ice10']

alph_inf = [0.1 ,0.1  ,0.1  ,0.1  ,0.1  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.2  ,0.18   ,0.06  , -1.0       , 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75]
alph_k   = [0.5 ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,None   ,None  ,None       ,None,None,None,None,None,None,None,None,None,None,None ]

files = sort(listdir_path(data_dir + mod_dir))[0:120]

lais = load_stash(files, LAI__code, 'lai' )
frac = load_stash(files, Frac_code, 'frac')
soilAlb = iris.load_cube(slAb_file, slAb_varn)

albedo = Albedo(frac, lais, soilAlb, dict(zip(tile_lev, alph_inf)), dict(zip(tile_lev, alph_k)))
cell_albedo  = albedo.cell()


def plotMapsTS(dat, figN, jbName, cmap, levels, labels = 'JFMAMJJASOND',
              mdat = None, nx = 6, ny = 3, running_mean = False, *args, **kw):
    if mdat is None: mdat = dat

    try: dat.units = 'days'
    except: pass

    plot_cubes_map(mdat, labels, cmap, levels, nx = 6, ny = 3,
                   cbar_yoff = 0.25, projection = None, *args, **kw)
    
    plt.subplot(4, 1, 4)
    
    tdat = dat if type(dat) == list else [dat]
    plot_cube_TS(tdat, running_mean, ylabel = unit)
    
    plt.title(jbName)  
    
    fig_name = 'figs/' + fign + '-' + figN + '-' +jbName + '.png'
    plt.savefig(fig_name)

    try: dat.var_name = dat.long_name = jbName
    except: pass
    return dat



def plotInterAnnual(dat, jbName, figN, mnthLength = 30, timeCollapse = iris.analysis.SUM,
                    *args, **kw):    
    if mnthLength > 1:
        mclim = dat[(mnthLength/2)::mnthLength].copy()

        for mn in range(mclim.shape[0]):
            md = mn * mnthLength
            mclim.data[mn] = dat[md:(md+mnthLength)].collapsed('time', timeCollapse).data
    else:
        mclim = dat
    aclim = mclim[6::12].copy()
    
    for yr in range(aclim.shape[0]):
        ym = yr * 12
        aclim.data[yr] = mclim[ym:(ym+12)].collapsed('time', timeCollapse).data    
        
    labels = [str(i)[10:14] for i in aclim.coord('time')]
    mclim = plotMapsTS(mclim, figN + 'IA', jbName, cmap, ann_levels,
                       labels = labels, mdat = aclim, totalMap = timeCollapse)
    return mclim, aclim, labels

plotInterAnnual(cell_albedo, mod_dir[0:7], fign, mnthLength = 1,
                timeCollapse = iris.analysis.MEAN)

def plotClimatology(dat, jbName, figN, mnthLength = 30,
                    timeCollapse = iris.analysis.SUM,  nyrNormalise = True, *args, **kw):
    ## convert to same as function above
    yrLength = 12 * mnthLength
   
    dclim = dat[0:yrLength].copy()
    

    ## convert to climatology
    nyrs = np.floor(dat.shape[0] / yrLength) if nyrNormalise else 1.0
    
    for t in range(0, yrLength):
        dclim.data[t] = dat[t::yrLength].collapsed('time', timeCollapse).data / nyrs
    
    if mnthLength > 1:
        mclim = dat[(mnthLength/2):yrLength:mnthLength].copy()
        for mn in range(0, 12):
            md = mn * 30
            mclim.data[mn] = dclim[md:(md+30)].collapsed('time', timeCollapse).data
    else:
        mclim = dclim

    mclim = plotMapsTS(mclim, figN + 'clim', jbName, cmap, clim_levels)
    return mclim, mclim, 'JFMAMJJASOND'


plotClimatology(cell_albedo, mod_dir[0:7], fign, mnthLength = 1,
                timeCollapse = iris.analysis.MEAN, nyrNormalise = False)

browser()

# see plot region in snow
