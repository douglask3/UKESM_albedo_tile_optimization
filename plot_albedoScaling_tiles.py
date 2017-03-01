import libs.import_iris
import iris
import numpy as np

import matplotlib.pyplot as plt
import cartopy.crs as ccrs


from   os                import listdir, getcwd, mkdir, path, walk
from   pylab             import sort
from   pdb               import set_trace as browser

from   libs              import git_info
from   libs.listdir_path import *
from   libs.weightedFuns import *
from   libs.which        import *
from   libs.nanRound     import *
from   libs.grid_area    import grid_area

data_dir      = 'data/u-aj523/'
tileFrac_file = 'data/N96e_GA7_17_tile_cci_reorder.anc'

tile_lev = np.array([101  ,102       ,103       ,201  ,202  ,3    ,301  ,302  ,4    ,401  ,
                     402  ,501  ,502  ,6      ,7     ,8          ,9])
tile_nme = np.array(['BD','TBE','tBE','NLD','NLE','C3G','C3C','C3P','C4G','C4C',
                     'C4P','SHD','SHE','Urban','Lake','Bare Soil','Ice'])

var_name = ['VIS', 'NIR']
stashCde = ['m01s01i270', 'm01s01i271']

files    = sort(listdir_path(data_dir))


def plotBox(dat, weights, N, n, title = '', maxy = 2, xlab = None):
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
    if xlab is None: xlab = np.repeat('', len(tile_nme))        
    plt.xticks(range(0, len(xlab)), xlab, fontsize = 8)  

    return dat



for var, code in zip(var_name, stashCde):
    stash_constraint = iris.AttributeConstraint(STASH = code)
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
        ww[ww < 0.0] = 0.0
        
        dat.append(dd)        
        weight.append(ww)
    
    plt.figure(figsize = (8, 12))

    mnVar = [weighted_avg_and_std(i,j) for i, j in zip(dat, weight)]
    
    
    mnVar = [nanRound(i, 2) for i in mnVar]
    
    labs = [i + '\n' + str(j[0]) + '\n' + str(j[1]) for i, j in zip(tile_nme, mnVar)]
    labs = [' \nMean\nStd'] + labs


    plotBox(dat, None  , 4, 1, title = 'None-weighted tile albedo scaling',
            maxy = None)
    plotBox(dat, None  , 4, 2, title = 'Zoomed in None-weighted tile albedo scaling',
            maxy = 2)
    
    dat = plotBox(dat, weight, 4, 3, title = 'Weighted tile albedo scaling',
                  maxy = None)
    plotBox(dat, None, 4, 4, title = 'Zoomed in weighted tile albedo scaling',
            maxy = 2, xlab = labs)
    
    git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
    plt.gcf().text(.05, .18, git, fontsize = 8)
    fname = 'figs/' + var + 'meanVar' + '.png'
    plt.savefig(fname, bbox_inches = 'tight')
    


