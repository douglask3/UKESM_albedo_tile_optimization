import iris
import numpy as np
from   os    import listdir, getcwd, mkdir, path, walk
from   pylab import sort
from   pdb   import set_trace as browser

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import cartopy.crs as ccrs
from   libs import git_info

def listdir_path(path):
    from os import listdir
    
    files = listdir(path)
    files = [path + i for i in files]
    return files

data_dir = 'data/'
mod_out = 'ag589/'

soil_fignm = 'soil'
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

def to_precision(x,p):
    import math
    """
    returns a string representation of x formatted with a precision of p

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
    """

    x = float(x)

    if x == 0.:
        return 0.0

    out = []

    if x < 0:
        out.append("-")
        x = -x

    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x/tens)

    if n < math.pow(10, p - 1):
        e = e -1
        tens = math.pow(10, e - p+1)
        n = math.floor(x / tens)
    if abs((n + 1.) * tens - x) <= abs(n * tens -x):
        n = n + 1

    if n >= math.pow(10,p):
        n = n / 10.
        e = e + 1

    m = "%.*g" % (p, n)

    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p -1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e+1])
        if e+1 < len(m):
            out.append(".")
            out.extend(m[e+1:])
    else:
        out.append("0.")
        out.extend(["0"]*-(e+1))
        out.append(m)

    return float("".join(out))


def hist_limits(dat, nlims, symmetrical = True):
    nlims0 = nlims
    for p in range(0,100 - nlims0):
        nlims = nlims0 + p
        
        lims = np.percentile(dat.data[~np.isnan(dat.data)], range(0, 100, 100/nlims))
 
        lims = [to_precision(i, 2) for i in lims]
        lims = np.unique(lims)
        if (len(lims) >= nlims0): return(lims)
    
    
    return(lims)

def plot_cube(cube, Ns, N, cmap):
    plt.subplot(Ns - 1, 2, N, projection=ccrs.Robinson())
    cube = cube.collapsed('time', iris.analysis.MEAN)
    
    #levels = MaxNLocator(nbins=15).tick_values(cube.data.min(), cube.data.max())
    cmap = plt.get_cmap(cmap)
    levels = hist_limits(cube, 7)
    
    norm = BoundaryNorm(levels, ncolors=cmap.N , clip=False)
    qplt.contourf(cube, levels = levels, cmap = cmap, norm = norm)
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
 
def open_plot_and_return(figName, codes, names, title,  units, cmap):
    fig_name = 'figs/' + figName + '.pdf'
    git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
    plt.figure(figsize = (12, 12))

    dat = load_group(codes, names)
    plot_cubes(dat, title,  units, cmap)

    plt.gcf().text(.6, .1, git)
    plt.savefig(fig_name)

open_plot_and_return(soil_fignm, soil_codes, soil_names, soil_title,  soil_units, soil_cmap)

