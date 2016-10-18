#############################################################################
## cfg                                                                     ##
#############################################################################

## General
data_dir = 'data/'
mod_out = 'ag589/'


## Soils
soil_fignm = 'soil'
soil_title = 'SOIL_CARBON_POOL'
soil_units = 'kg m-2'
soil_names = ['DPM', 'RPM', 'BIO', 'HUM', 'VEGC']
soil_codes = ['m01s00i466', 'm01s00i467', 'm01s00i468', 'm01s00i469', 'm01s19i002']
soil_cmap  = 'brewer_GnBu_09'

## Wood Prod Pools
Wood_fignm = 'woodProd'
Wood_title = 'WOOD_PRODUCT'
Wood_units = 'kg m-2'
Wood_names = ['FAST', 'MEDIUM', 'SLOW']
Wood_codes = ['m01s00i287', 'm01s00i288', 'm01s00i289']
Wood_cmap  = 'brewer_YlOrBr_09'

## Fluxes
Flux_fignm = 'Fluxes'
Flux_title = 'FLUXES'
Flux_units = 'kg m-2 s-1'
Flux_names = ['NPP', 'Resp', 'Wood_prod']
Flux_dirct = ['in' , 'out', 'out']
Flux_codes = ['m01s03i262', 'm01s03i293', 'm01s19i042']
Flux_cmap  = 'brewer_BrBG_11'

# uag 745
#############################################################################
## libs                                                                    ##
#############################################################################
import iris
import numpy as np
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
def load_group(codes, names, dat = None, dirct = None, **kw):
    if (dat is None):
        dat = [load_stash(files, code, name, **kw) for code, name in zip(codes, names)]
    
    tot = dat[0].copy()
    if (dirct is None):        
        for i in dat[1:]: tot.data += i.data
    else:
        if (dirct[0] != 'in'):
            tot.data = -tot.data
        
        for i in range(1, len(dat)):
            if (dirct[i] == 'in'):
                tot.data += dat[i].data
            else:
                tot.data -= dat[i].data

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
flux = open_plot_and_return(Flux_fignm, Flux_title, Flux_codes, Flux_names,  Flux_units, Flux_cmap, dirct = Flux_dirct)

def deltaT(cubes):
    for i in range(cubes.coord('time').shape[0] -1 , 0 , -1):
        cubes.data[i] = (cubes.data[i] - cubes.data[i - 1]) * 4 / (360 * 24 * 60 * 60)
    cubes.data[0] -= cubes.data[0] 
    return cubes

soil = deltaT(soil)
wood = deltaT(wood)

flux.data[0] -= flux.data[0]

cmap = ['brewer_RdYlBu_11', 'brewer_PuOr_11', Flux_cmap, 'brewer_RdYlBu_11']

open_plot_and_return('overall', 'overall', cmap = cmap, dat = [soil, wood, flux])
