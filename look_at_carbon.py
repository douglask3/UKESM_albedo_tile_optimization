import iris
import numpy as np
from   os    import listdir, getcwd, mkdir, path, walk
from   pylab import sort
from   pdb   import set_trace as browser

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def listdir_path(path):
    from os import listdir
    
    files = listdir(path)
    files = [path + i for i in files]
    return files

data_dir = 'data/'
mod_out = 'ag589/'

soil_title = 'SOIL CARBON POOL'
soil_units = 'KG C / M2'
soil_names = ['DPM', 'BIO', 'HUM']
soil_codes = ['m01s00i466', 'm01s00i467', 'm01s00i468', 'm01s00i469']
soil_cmap  = 'brewer_GnBu_09'

files = sort(listdir_path(data_dir + mod_out))

def load_stash(code, name):
    print code
    stash_constraint = iris.AttributeConstraint(STASH = code)
    cube = iris.load_cube(files, stash_constraint)
    cube.long_name = name
    return cube    

def load_group(codes, names):
    mod = [load_stash(code, name) for code, name in zip(codes, names)]
    
    tot = sum(mod)
    tot.long_name = 'total'   
    mod.append(tot)
    
    return mod

def grid_area(cube):
    if cube.coord('latitude').bounds is None:
        cube.coord('latitude').guess_bounds()
        cube.coord('longitude').guess_bounds()
    return iris.analysis.cartography.area_weights(cube)    

def cube_TS(cube):
    grid_areas = grid_area(cube)
    return cube.collapsed(['latitude', 'longitude'], iris.analysis.SUM, weights = grid_areas)

def plot_cube_TS(cubes, units):    
    cubes = [cube_TS(cube) for cube in cubes]    
    
    for cube in cubes: iplt.plot(cube, label = cube.name())
    plt.legend(ncol=2)
    plt.grid(True)    
    plt.axis('tight')
    plt.gca().set_ylabel(units, fontsize=16)
        

def plot_cube(cube, Ns, N, cmap):
    print N, Ns
    plt.subplot(Ns - 1, 2, N, projection=ccrs.Robinson())
    cube = cube.collapsed('time', iris.analysis.MEAN)
    qplt.contourf(cube, 8, cmap = cmap)
    plt.gca().coastlines()


def plot_cubes_map(cubes, *args):
    nplots = len(cubes)
    for i in range(0, nplots - 1): 
        print i 
        plot_cube(cubes[i], nplots, i * 2 + 1, *args)
    
    plot_cube(cubes[i + 1], nplots, 2, *args)

def plot_cubes(cubes, title, units, *args):
    nplots = len(cubes)

    plot_cubes_map(cubes, *args)  
    
    plt.subplot(nplots - 1, 2, 4)
    plot_cube_TS(cubes, units)      
    
    plt.gcf().suptitle(title, fontsize=18, fontweight='bold')
 

fig_name = 'figs/' + 'yay.pdf'
plt.figure(figsize = (12, 12))

soil = load_group(soil_codes, soil_names)
plot_cubes(soil, soil_title,  soil_units, soil_cmap)

plt.savefig(fig_name)
