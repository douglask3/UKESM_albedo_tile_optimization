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

data_dir      = 'data/u-aj523/'
tileFrac_file = 'data/N96e_GA7_17_tile_cci_reorder.anc'


tile_lev = np.array([101  ,102       ,103       ,201  ,202  ,3    ,301  ,302  ,4    ,401  ,
                     402  ,501  ,502  ,6      ,7     ,8          ,9])
tile_nme = np.array(['BD','TBE','tBE','NLD','NLE','C3G','C3C','C3P','C4G','C4C',
                     'C4P','SHD','SHE','Urban','Lake','Bare Soil','Ice'])

var_name = ['VIS', 'NIR']
stashCde = ['m01s01i270', 'm01s01i271']

files    = sort(listdir_path(data_dir))

def which(a, b):
    return([i for i in range(0, len(a)) if a[i] == b])

def grid_area(cube):
    if cube.coord('latitude').bounds is None:
        cube.coord('latitude').guess_bounds()
        cube.coord('longitude').guess_bounds()
    return iris.analysis.cartography.area_weights(cube)

def weight_array(ar, wts):
        zipped = zip(ar, wts)
        weighted = []
        for i in zipped:
            for j in range(i[1]):
                weighted.append(i[0])
        return weighted

def weightedBoxplot(data, weights = None, minW = 0.0001, *args, **kw):
    def sampleDat(dat, weight):
        weight[weight < minW] = 0.0
        weight = (weight / minW)
        weight = np.around(weight)
        weight = weight.astype(int)
        return(weight_array(dat, weight))
    if (weights is not None):
        data = [sampleDat(d, w) for d, w in zip(data, weights)]

    return plt.boxplot(data, *args, **kw), data

def plotBox(dat, weights, N, n, title = '', maxy = 2, xlab = False):
    fig = plt.subplot(N, 1, n)

    plt.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)

    bp, dat = weightedBoxplot(dat, weights, notch=0, sym='+', vert=1, whis=1.5)
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
        mn = [np.around(np.mean(i), decimals = 2) for i in dat]
        sd = [np.around(np.std (i), decimals = 2) for i in dat]
        labs = [i + '\n' + str(j) + '\n' + str(k) for i, j, k in zip(tile_nme, mn, sd)]
        labs = [' \nMean\nStd'] + labs 
    else:
        labs = np.repeat('', len(tile_nme))
    plt.xticks(range(0, len(labs)), labs, fontsize = 8)  

    return dat



for var, code in zip(var_name, stashCde):
    stash_constraint = iris.AttributeConstraint(STASH = 'm01s01i270')
    dats     = iris.load_cube(files, stash_constraint)
    weights  = iris.load_cube(tileFrac_file)

    cTiles   = dats.coords('pseudo_level')[0].points
    dat      = []
    weight   = []
    gridArea = grid_area(weights[0])
    gridArea = gridArea / gridArea.max()
    for tile in tile_lev:
        print(tile)
        i = which(cTiles, tile)[0]
        
        dd = dats[i].data.data.flatten()

        ww = weights[i].data * gridArea
        try:
            ww = np.tile(ww.data.flatten(),dats[i].shape[0])
        except:
            ww = np.tile(ww.flatten(),dats[i].shape[0])

        msk = dd >= 0.0        
        dd = dd[msk]
        ww = ww[msk]
        
        dat.append(dd)        
        weight.append(ww)
    
    plt.figure(figsize = (8, 12))

    plotBox(dat, None  , 4, 1, title = 'None-weighted tile albedo scaling',
            maxy = None)
    plotBox(dat, None  , 4, 2, title = 'Zoomed in None-weighted tile albedo scaling',
            maxy = 2)
    
    plotBox(dat, weight, 4, 3, title = 'Weighted tile albedo scaling',
            maxy = None)
    plotBox(dat, weight, 4, 4, title = 'Zoomed in weighted tile albedo scaling',
            maxy = 2, xlab = True)
    
    git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
    plt.gcf().text(.05, .18, git, fontsize = 8)
    fname = 'figs/' + var + 'meanVar' + '.png'
    plt.savefig(fname, bbox_inches = 'tight')
    


