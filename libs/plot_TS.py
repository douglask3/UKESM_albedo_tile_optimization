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

### Running mean/Moving average
def running_mean(l, N):
    sum = 0
    result = list( 0 for x in l)

    for i in range( 0, N ):
        sum = sum + l[i]
        result[i] = sum / (i+1)

    for i in range( N, len(l) ):
        sum = sum - l[i-N] + l[i]
        result[i] = sum / N

    return result

def cube_TS(cube, running_mean = False):
    grid_areas = grid_area(cube)
    cube = cube.collapsed(['latitude', 'longitude'], iris.analysis.SUM, weights = grid_areas)
    if (running_mean): cube.data = running_mean(cube.data, 12)
    return cube   

def plot_cube_TS(cubes, running_mean):    
    cubes = [cube_TS(cube, running_mean) for cube in cubes]    
    
    for cube in cubes: iplt.plot(cube, label = cube.name())
    plt.legend(ncol = 2, loc = 0)
    plt.grid(True)    
    plt.axis('tight')
    
    plt.gca().set_ylabel(cubes[0].units, fontsize=16)
