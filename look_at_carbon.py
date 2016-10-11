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


data_dir = 'data/'
mod_out = 'ag589/'

soil_fignm = 'soil'
soil_title = 'SOIL CARBON POOL'
soil_units = 'KG C / M2'
soil_names = ['DPM', 'BIO', 'HUM']
soil_codes = ['m01s00i466', 'm01s00i467', 'm01s00i468', 'm01s00i469']
soil_cmap  = 'brewer_GnBu_09'

files = sort(listdir_path(data_dir + mod_out))

def load_group(codes, names):
    mod = [load_stash(files, code, name) for code, name in zip(codes, names)]
    
    tot = sum(mod)
    tot.long_name = 'total'   
    mod.append(tot)
    
    return mod


def plot_cubes(cubes, title, units, *args):
    nplots = len(cubes)

    plot_cubes_map(cubes, *args)  
    
    plt.subplot(nplots - 1, 2, 4)
    plot_cube_TS(cubes, units)      
    
    plt.gcf().suptitle(title, fontsize=18, fontweight='bold')
 
def open_plot_and_return(figName, codes, names, title,  units, cmap):
    fig_name = 'figs/' + figName + '.pdf'
    git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
    plt.figure(figsize = (12, 12))

    dat = load_group(codes, names)
    plot_cubes(dat, title,  units, cmap)

    plt.gcf().text(.6, .1, git)
    plt.savefig(fig_name)

open_plot_and_return(soil_fignm, soil_codes, soil_names, soil_title,  soil_units, soil_cmap)

