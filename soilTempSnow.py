import libs.import_iris
import iris.plot      as iplt
import iris.quickplot as qplt

import matplotlib.pyplot as plt
import matplotlib.colors as colours
from   pylab             import *
import matplotlib.cm     as mpl_cm
import cartopy.crs       as ccrs

from os import listdir, getcwd, mkdir, path
from pdb import set_trace as browser

from libs import git_info
from libs.listdir_path import *
from libs.load_stash import *
from libs.plotSWoverSW import *
from libs.plotRegions import *

dataDir  = 'data/bareSoilEffect/'
fracCode = 'm01s19i013'
snowCode = 'm01s08i023'
tempCode = 'm01s00i024'

git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
cmap = plt.cm.YlOrBr_r
snow_percentiles = range(0, 100, 1)

frac = load_stash_dir(dataDir, fracCode)
snow = load_stash_dir(dataDir, snowCode)[9]
temp = load_stash_dir(dataDir, tempCode)[9]

fracMin = 0.0
fracMax = 1.0
tempMin = -15
tempMax = 15

xi = np.linspace(0, 1.1, 110)
yi = np.linspace(tempMin, tempMax, 121)

fig_file = 'figs/frac_temp_snow.png'

def scatterByVegType(zCube, y, z, i, name, xticks = False, yticks = False):
    
    pfts = [np.where(zCube.coord('pseudo_level').points == pft)[0][0] for pft in i]
    veg = iris.cube.CubeList([zCube[pft] for pft in pfts]).merge()[0]
    try:
        veg = veg.collapsed('pseudo_level', iris.analysis.SUM)
    except: 
        pass
    veg = veg[9]
    
    x = veg.data.flatten()
    
    #plt.colorbar()  # draw colorbar
    # plot data points.
    col = z.copy()
    levels = np.percentile(z[z > 0.0], snow_percentiles)   
    col[:] = 0.0     
    
    for lev in levels:  col[z > lev] += 100.0/len(levels) 
    
    zi = griddata(x, y, np.log10(z), xi, yi, interp='linear')

    #CS = plt.contour(xi, yi, zi, 15, linewidths=0.5, colors='k')
    CS = plt.contourf(xi, yi, zi, 15, vmax=abs(zi).max(), vmin=-abs(zi).max(), cmap = plt.cm.gray)
    
    plt.scatter(x, y, c = col, cmap = cmap, marker = 'o', linewidth = 0.0)
    plt.xlim(fracMin, fracMax)
    plt.ylim(tempMin, tempMax)
   
    plt.title(name + '-' + str(i))
    plt.grid(True)
    if not xticks: plt.gca().get_xaxis().set_ticklabels([])
    if not yticks: plt.gca().get_yaxis().set_ticklabels([])
    #plt.xlabel('')
    #plt.ylabel(')

def pltRegion(plotn = 0, *args, **kw):
    snowR = ExtractLocation(snow, *args, **kw).cubes
    tempR = ExtractLocation(temp, *args, **kw).cubes
    fracR = ExtractLocation(frac, *args, **kw).cubes
    
    
    y = tempR.data.flatten() - 273.15
    z = snowR.data.flatten()

    def scatterByVegTypeRegion(N, *args, **kw):
        plt.subplot(4, 2, N + plotn)
        scatterByVegType(fracR, y, z, *args, **kw)
        
    scatterByVegTypeRegion(1, [3, 301, 302], 'C3 grass', yticks = True)
    scatterByVegTypeRegion(3, [4, 401, 402], 'C4 grass', yticks = True)
    scatterByVegTypeRegion(5, [3, 301, 302, 4, 401, 402], 'Grass', yticks = True)
    scatterByVegTypeRegion(7, [8], 'Bare Soil', xticks = True, yticks = True)

fig = plt.figure(figsize = (12,14))

pltRegion(0, east = None, west = None , south = None, north = None)
pltRegion(1, east = 125.0, west = 55.0, south = 40.0, north = 52.0)

fig.text(0.33, 0.96, 'Global', ha='center', va='center', fontsize = 20)
fig.text(0.67, 0.96, 'Asia5', ha='center', va='center', fontsize = 20)

fig.text(0.5, 0.04, '% Cover', ha='center', va='center')
fig.text(0.06, 0.5, 'Temperature ($^\circ$C)', ha='center', va='center', rotation='vertical')

m = mpl_cm.ScalarMappable(cmap = cmap)
m.set_array(snow_percentiles)

fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
#fig.colorbar(im, cax=cbar_ax)

cb = fig.colorbar(m, cax=cbar_ax)
cb.set_label('Snow mass %ile')

plt.gcf().text(.18, .05, git, fontsize = 8)
plt.savefig(fig_file, bbox_inches = 'tight')





