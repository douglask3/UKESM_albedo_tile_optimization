#############################################################################
## cfg                                                                     ##
#############################################################################
import numpy as np
## General
data_dir = 'data/'
mod_out = 'ah410/'

yr2sec = 1.0 / (60 * 60 * 24 * 360)

## Soils
soil_fignm = 'soil'
soil_title = 'SOIL_CARBON_POOL'
soil_units = 'kg m-2'
soil_names = ['DPM'       , 'RPM'       , 'BIO'       , 'HUM'       , 'VEGC']
soil_codes = ['m01s19i021', 'm01s19i022', 'm01s19i023', 'm01s19i024', 'm01s19i002']
soil_cmap  = 'brewer_GnBu_09'

## Wood Prod Pools
Wood_fignm = 'woodProd'
Wood_title = 'WOOD_PRODUCT'
Wood_units = 'kg m-2'
Wood_names = ['FAST'      , 'MEDIUM'    , 'SLOW']
Wood_codes = ['m01s19i032', 'm01s19i033', 'm01s19i034']
Wood_cmap  = 'brewer_YlOrBr_09'

## Wood Fluxes
WdFl_fignm = 'Wood_fluxes'
WdFl_title = 'WOOD FLUXES'
WdFl_units = 'kg m-2 s-1'
WdFl_names = ['FAST-IN'   , 'MEDIUM-IN' , 'SLOW-IN'   , 'FAST-OUT'  , 'MEDIUM-OUT', 'SLOW-OUT']
WdFl_codes = ['m01s19i036', 'm01s19i037', 'm01s19i038', 'm01s19i039', 'm01s19i040', 'm01s19i041']
WdFl_scale = yr2sec * np.array([1.0, 1.0, 1.0, -1.0, -1.0, -1.0])
WdFl_cmap  = 'brewer_BrBG_11'


## Fluxes
Flux_fignm = 'Fluxes'
Flux_title = 'FLUXES'
Flux_units = 'kg m-2 s-1'
Flux_names = ['NPP'       , 'Resp', 'Wood_prod']
Flux_codes = ['m01s19i009', 'm01s19i011', 'm01s19i010']
Flux_scale = yr2sec * np.array([1.0, -1.0, -1.0])
Flux_cmap  = 'brewer_BrBG_11'


#############################################################################
## libs                                                                    ##
#############################################################################

import libs.import_iris #comment out this line if not run on CEH linux box
import iris

from   pylab import sort      
import matplotlib.pyplot as plt

from   libs              import git_info
from   libs.plot_maps    import *
from   libs.plot_TS      import *
from   libs.listdir_path import *
from   libs.load_stash   import *

from   pdb   import set_trace as browser  

#############################################################################
## Funs                                                                    ##
#############################################################################
def load_group(codes, names, dat = None, scale = None, **kw):
    if (dat is None):        
        dat = [load_stash(files, code, name, **kw) for code, name in zip(codes, names)]
        
    for i in range(0, len(dat)):
            if (dat[i].coords()[0].long_name == 'pseudo_level'):
                print('warning: ' + names[i] + ' has pseudo_levels')
                dat[i] = dat[i].collapsed('pseudo_level', iris.analysis.MEAN)             
    
    if (scale is not None):
        for i in range(0, len(dat)):  dat[i].data = dat[i].data * scale[i]    
   
    tot = dat[0].copy()
    for i in dat[1:]: tot.data += i.data

    tot.var_name  = 'total'
    tot.long_name = 'total'   
    dat.append(tot)
    
    return dat


def plot_cubes(cubes, title, *args):
    nplots = len(cubes)    
    plot_cubes_map(cubes, *args)  
    
    plt.subplot(nplots - 1, 2, 4)
    plot_cube_TS(cubes)      
    
    plt.gcf().suptitle(title, fontsize=18, fontweight='bold')
 
def open_plot_and_return(figName, title,
                         codes = None, names = None,  units  = None,
                         cmap = 'brewer_Greys_09', **kw):
    fig_name = 'figs/' + figName + '.pdf'
    git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
    
    dat = load_group(codes, names, units = units, **kw)
    
    plt.figure(figsize = (15, 5 * (len(dat) - 1)))
    plot_cubes(dat, title, cmap)

    plt.gcf().text(.5, .1, git)
    plt.savefig(fig_name)
    
    dat[-1].long_name = title
    
    return dat[-1]


#############################################################################
## Run                                                                     ##
#############################################################################
files = sort(listdir_path(data_dir + mod_out))

soil = open_plot_and_return(soil_fignm, soil_title, soil_codes, soil_names,  soil_units, soil_cmap)
wood = open_plot_and_return(Wood_fignm, Wood_title, Wood_codes, Wood_names,  Wood_units, Wood_cmap)
wdfl = open_plot_and_return(WdFl_fignm, WdFl_title, WdFl_codes, WdFl_names,  WdFl_units, WdFl_cmap, scale = WdFl_scale)

flux = open_plot_and_return(Flux_fignm, Flux_title, Flux_codes, Flux_names,  Flux_units, Flux_cmap, scale = Flux_scale)

def deltaT(cubes):
    for i in range(cubes.coord('time').shape[0] -1 , 0 , -1):
        cubes.data[i] = (cubes.data[i] - cubes.data[i - 1]) * 4 / (360 * 24 * 60 * 60)
    cubes.data[0] -= cubes.data[0] 
    return cubes

soil = deltaT(soil)
wood = deltaT(wood)

flux.data[0 ] -= flux.data[0 ]
flux.data[1:] =- flux.data[1:]
wdfl.data[0 ] -= wdfl.data[0 ]
wdfl.data[1:] =- wdfl.data[1:]

cmap = ['brewer_RdYlBu_11', 'brewer_PuOr_11', Flux_cmap, Flux_cmap,  'brewer_RdYlBu_11']

open_plot_and_return('overall', 'overall', cmap = cmap, dat = [soil, wood, wdfl, flux])
