import iris
import numpy as np
import cartopy.crs as ccrs

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable
from libs.to_precision import *
from pdb import set_trace as browser
from numpy import inf
import math

from   libs              import git_info

def plot_lonely_cube(cube, N = None, M = None, n = None, levels = [0], extend = 'neither', colourbar = True, *args, **kw):

    cf = plot_cube(cube, N,  M, n, levels = levels, extend = extend, *args, **kw)
    if colourbar: 

        addColorbar(cf, levels, extend = extend)
    plt.tight_layout()
    return cf
    
def addColorbar(cf, ticks, *args, **kw):
    cb = plt.colorbar(cf, orientation='horizontal', ticks = ticks, *args, **kw)
    cb.ax.set_xticklabels(ticks)
    return cb

def plot_cube(cube, N, M, n, cmap, levels, extend = 'neither', projection = ccrs.Robinson(),
              grayMask = False):
    
    if n is None:
        ax = plt.axes(projection = projection)
    else:
        ax = plt.subplot(N, M, n, projection = projection)

    ax.set_title(cube.long_name)

    cmap = plt.get_cmap(cmap)
    
    
    levelsi = [i for i in levels]
    
    if extend == "max" or extend == "both": levelsi += [9E9]
    if extend == "min" or extend == "both": levelsi = [-9E9] + levelsi

    if extend == "max" or extend == "min":
        norm = BoundaryNorm(levelsi, ncolors=cmap.N)
    else:
        norm = BoundaryNorm(levelsi, ncolors=cmap.N)
    
    if grayMask: plt.gca().patch.set_color('.25')
    try:
        cf = iplt.pcolormesh(cube, cmap = cmap, norm = norm) 
    except:
        cf = iplt.pcolormesh(cube, cmap = cmap) 
    
    plt.gca().coastlines()

    return cf


def plot_cubes_map(cubes, nms, cmap, levels, extend = 'neither',
                   figName = None, units = '', nx = None, ny = None, 
                   cbar_yoff = 0.0, figXscale = 1.0, figYscale = 1.0, 
                   totalMap = None, *args, **kw):
    
    try:
        cubeT =cubes.collapsed('time', totalMap)
        nms = [i for i in nms]
        nms.append('Total')
    except: cubeT = None  

    try: cubes = [cubes[i] for i in range(0, cubes.shape[0])]
    except: pass
    
    if cubeT is not None: cubes.append(cubeT)
    
    for i in range(0, len(cubes)):  cubes[i].long_name = nms[i]
    nplts = len(cubes)
    if nx is None and ny is None:
        nx = int(math.sqrt(nplts))
        ny = math.ceil(nplts / float(nx))
        nx = nx + 1.0
    elif nx is None:   
        nx = math.ceil(nplts / float(ny)) + 1
    elif ny is None:
        ny = math.ceil(nplts / float(nx))
    
    plt.figure(figsize = (nx * 2 * figXscale, ny * 4 * figYscale))

    for i in range(0, len(cubes)):         
        cmapi = cmap if (type(cmap) is str) else cmap[i]
        cf = plot_cube(cubes[i], nx, ny, i + 1, cmapi, levels, extend, *args, **kw)

    colorbar_axes = plt.gcf().add_axes([0.15, cbar_yoff + 0.5 / nx, 0.7, 0.15 / nx])
    cb = addColorbar(cf, levels, colorbar_axes, extend = extend)
    cb.set_label(units)

    plt.tight_layout()
    if (figName is not None):
        if figName == 'show':
            plt.show()
        else :
            print(figName)
            git = 'rev:  ' + git_info.rev + '\n' + 'repo: ' + git_info.url
            plt.gcf().text(.05, .95, git, rotation = 270, verticalalignment = "top")
            plt.savefig(figName, bbox_inches='tight')
            plt.clf()



