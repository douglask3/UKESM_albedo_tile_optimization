#############################################################################
## cfg                                                                     ##
#############################################################################

## General
data_dir = 'data/'
mod_out = 'ag589/'


## Soils
soil_fignm = 'soil'
soil_title = 'SOIL CARBON POOL'
soil_units = 'kg m-2'
soil_names = ['DPM', 'RPM', 'BIO', 'HUM']
soil_codes = ['m01s00i466', 'm01s00i467', 'm01s00i468', 'm01s00i469']
soil_cmap  = 'brewer_GnBu_09'

## Wood Prod Pools
Wood_fignm = 'woodProd'
Wood_title = 'WOOD PRODUCT'
Wood_units = 'kg m-2'
Wood_names = ['FAST', 'MEDIUM', 'SLOW']
Wood_codes = ['m01s00i287', 'm01s00i288', 'm01s00i289']
Wood_cmap  = 'brewer_YlOrBr_09'

## Fluxes
Flux_fignm = 'Fluxes'
Flux_title = 'FLUXES'
Flux_units = 'kg m-2 s-1'
Flux_names = ['NPP', 'Resp', 'Wood_prod']
Flux_codes = ['m01s03i262', 'm01s03i293', 'm01s19i042']
Flux_cmap  = 'brewer_BuPu_09'

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
def load_group(codes, names, **kw):
    mod = [load_stash(files, code, name, **kw) for code, name in zip(codes, names)]
    
    tot = mod[0].copy()
    for i in mod[1:]: tot.data += i.data
    
    tot.var_name  = 'total'
    tot.long_name = 'total'   
    mod.append(tot)
    
    return mod


def plot_cubes(cubes, title, *args):
    nplots = len(cubes)

    plot_cubes_map(cubes, *args)  
    
    plt.subplot(nplots - 1, 2, 4)
    plot_cube_TS(cubes)      
    
    plt.gcf().suptitle(title, fontsize=18, fontweight='bold')
 
def open_plot_and_return(figName, codes, names, title,  units, cmap):
    fig_name = 'figs/' + figName + '.pdf'
    git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
    
    dat = load_group(codes, names, units = units)
    
    plt.figure(figsize = (12, 4 * (len(dat) - 1)))
    plot_cubes(dat, title, cmap)

    plt.gcf().text(.5, .1, git)
    plt.savefig(fig_name)
    return dat[-1]


#############################################################################
## Run                                                                     ##
#############################################################################
files = sort(listdir_path(data_dir + mod_out))
soil = open_plot_and_return(soil_fignm, soil_codes, soil_names, soil_title,  soil_units, soil_cmap)
wood = open_plot_and_return(Wood_fignm, Wood_codes, Wood_names, Wood_title,  Wood_units, Wood_cmap)
flux = open_plot_and_return(Flux_fignm, Flux_codes, Flux_names, Flux_title,  Flux_units, Flux_cmap)

