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

frac = load_stash_dir(dataDir, fracCode)
snow = load_stash_dir(dataDir, snowCode)[9]
temp = load_stash_dir(dataDir, tempCode)[9]

fracMin = 0.0
fracMax = 1.0
tempMin = -15
tempMax = 15

y = temp.data.flatten() - 273.15
z = snow.data.flatten()
xi = np.linspace(0, 1.1, 110)
yi = np.linspace(tempMin, tempMax, 121)

def scatterByVegType(i, name):
    veg = frac[frac.coord('pseudo_level').points == i][0][9]
    x = veg.data.flatten()
    
    #plt.colorbar()  # draw colorbar
    # plot data points.
    col = z.copy()
    levels = np.percentile(z[z > 0.0], range(0, 100, 1))   
    col[:] = 0.0     
    
    for lev in levels:  col[z > lev] += 100.0/len(levels) 
    
    zi = griddata(x, y, np.log10(z), xi, yi, interp='linear')

    #CS = plt.contour(xi, yi, zi, 15, linewidths=0.5, colors='k')
    CS = plt.contourf(xi, yi, zi, 15, vmax=abs(zi).max(), vmin=-abs(zi).max(), cmap = plt.cm.gray)
    
    plt.scatter(x, y, c = col, cmap = cmap, marker = 'o', linewidth = 0.0)
    plt.xlim(fracMin, fracMax)
    plt.ylim(tempMin, tempMax)
    plt.title(name + '-' + str(i))
    #m = mpl_cm.ScalarMappable(cmap=plt.cm.coolwarm)
    #m.set_array(levels)
    cb = plt.colorbar()
    cb.set_label('Snow mass %ile')
    plt.grid(True)
    plt.xlabel('% cover')
    plt.ylabel('Temperature ($^\circ$C)')
    plt.show()


scatterByVegType(8, 'Bare Soil')

browser()





