import iris
import numpy as np
import cartopy.crs as ccrs

import iris.plot as iplt
import matplotlib.pyplot as plt
from pdb import set_trace as browser


def grid_area(cube):
    if cube.coord('latitude').bounds is None:
        cube.coord('latitude').guess_bounds()
        cube.coord('longitude').guess_bounds()
    return iris.analysis.cartography.area_weights(cube)    

def cube_TS(cube):
    grid_areas = grid_area(cube)
    return cube.collapsed(['latitude', 'longitude'], iris.analysis.SUM, weights = grid_areas)

def plot_cube_TS(cubes):    
    cubes = [cube_TS(cube) for cube in cubes]    
    
    for cube in cubes: iplt.plot(cube, label = cube.name())
    plt.legend(ncol=2)
    plt.grid(True)    
    plt.axis('tight')
    
    plt.gca().set_ylabel(cubes[0].units, fontsize=16)
