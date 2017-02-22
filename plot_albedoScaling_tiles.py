import libs.import_iris
import iris
from libs import git_info
from libs.listdir_path import *
import numpy as np
from   os    import listdir, getcwd, mkdir, path, walk
from   pylab import sort
from   pdb   import set_trace as browser

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

data_dir = 'data/u-aj523/'


tile_lev = np.array([101  ,102       ,103       ,201  ,202  ,3    ,301  ,302  ,4    ,401  ,402  ,501  ,502  ,6      ,7     ,8          ,9])
tile_nme = np.array(['BLD','BLE_Trop','BLE_Temp','NLD','NLE','C3G','C3C','C3P','C4G','C4C','C4P','SHD','SHE','Urban','Lake','Bare Soil','Ice'])

var_name = ['VIS', 'NIR']
stashCde = ['m01s01i270', 'm01s01i271']

files = sort(listdir_path(data_dir))

def which(a, b):
    return([i for i in range(0, len(a)) if a[i] == b])

def weightedBoxplot(dat, weights = None, *args, **kw):
    if (weights is None): return(plt.boxplot(dat, *args, **kw))
    browser()
    

def plotBox(dat, weights, N, n, title = '', maxy = 2, xlab = True):
    fig = plt.subplot(N, 1, n)
    plt.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)

    bp = weightedBoxplot(dat, weights, notch=0, sym='+', vert=1, whis=1.5)
    ax1 = plt.gca()

    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='red', marker='+')

    # Add a horizontal grid to the plot, but make it very light in color
    # so we can use it for reading data values but not be distracting
    ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
                   alpha=0.5)

    
# Hide these grid behind plot objects
    ax1.set_axisbelow(True)
    ax1.set_title(title)
    ax1.set_xlabel(' ')
    ax1.set_ylabel('Scaling')
    
    # Set the axes ranges and axes labels
    ax1.set_ylim(0, maxy)
    if xlab: 
        mn = [i.mean() for i in dat]
        labs = [i + ' - ' +str(j) for i,j in zip(tile_nme, mn)]
        xtickNames = plt.setp(ax1, xticklabels = labs)
    else:        
        xtickNames = plt.setp(ax1, xticklabels = np.repeat('', len(tile_nme)))

    plt.setp(xtickNames, rotation=45, fontsize=8)


for var, code in zip(var_name, stashCde):
    stash_constraint = iris.AttributeConstraint(STASH = 'm01s01i270')
    cube = iris.load_cube(files, stash_constraint)
    cTiles = cube.coords('pseudo_level')[0].points
    dat = []
    for tile in tile_lev:
        print(tile)
        i = which(cTiles, tile)[0]
        print(i)
        dat.append(cube[i].data.compressed())
    
    plotBox(dat, None, 2, 1, title = 'None-weighted tile albedo scaling', maxy = None, xlab = False)
    plotBox(dat, None, 2, 2, title = 'Zoomed in None-weighted tile albedo scaling', maxy = 2)
    
    git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
    plt.gcf().text(.05, .05, git, fontsize = 8)
    fname = 'figs/' + var + 'meanVar' + '.png'
    plt.savefig(fname, bbox_inches = 'tight')
    


