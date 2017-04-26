import iris
import numpy as np
import cartopy.crs as ccrs

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from to_precision import *
from pdb import set_trace as browser
from numpy import inf
import math

from   libs              import git_info




def plot_cube(cube, N, M, n, cmap, levels, extend, projection = ccrs.Robinson()):
    ax = plt.subplot(N, M, n, projection = projection)
    ax.set_title(cube.long_name)

    cmap = plt.get_cmap(cmap)
    
    if (extend =='max'): 
        norm = BoundaryNorm(levels, ncolors=cmap.N - 1)
    else:
        norm = BoundaryNorm(levels, ncolors=cmap.N)
    
    cf = iplt.contourf(cube, levels = levels, cmap = cmap, norm = norm, extend = extend) 
    #if (n == 5): browser()
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
    colorbar = plt.colorbar(cf, colorbar_axes, orientation='horizontal')
    colorbar.set_label(units)
    
    git = 'rev:  ' + git_info.rev + '\n' + 'repo: ' + git_info.url
    plt.gcf().text(.05, .95, git, rotation = 270, verticalalignment = "top")
    
    if (figName is not None):
        if figName == 'show':
            plt.show()
        else :
            print(figName)
            plt.savefig(figName, bbox_inches='tight')
            plt.clf()

