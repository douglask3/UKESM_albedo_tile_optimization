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

obs = 'data/qrparm_func_orca1_esmf_13_tile_0.1.anc'
mod = 'data/u-aq226/apm/'

obs = iris.load(obs)[0]
mod = load_stash_dir(mod, 'm01s19i015')[:,108:120]

obs = obs.collapsed('time', iris.analysis.MEAN)
mod = mod.collapsed('time', iris.analysis.MEAN)

dcmap = 'BrBG'
cmap  = 'PuBuGn'

levels = [0, 0.01, 0.1, 1, 5, 10, 20, 30]
dlevels = [-30, -20, -10,-5 , -1, -0.5, -0.2, -0.1, 0.1, 0.2, 0.5, 1, 2, 5, 6, 8]

tile_names = ['BD','TBE','tBE','NLD','NLE','C3G','C3C','C3P','C4G','C4C','C4P','SHD','SHE']
tile_codes = [101 , 102 , 103 , 201 , 202 , 3   , 301 , 302 , 4   , 401 , 402 , 501 , 502 ]

index = obs.coord('pseudo_level').points
index = [np.where(index == i)[0][0] for i in tile_codes]

obs = [obs[i] for i in index]
mod = [mod[i] for i in index]

def pltTiles(cubes, cmapi, levelsi, figName):
    plot_cubes_map(cubes, tile_names, cmapi, levelsi, extend = 'both',
                   figName = figName, figXscale = 4.0, projection = None)


diff = [i.copy() for i in mod]
for i,j in zip(diff, obs): i.data -= j.data

pltTiles(obs, cmap, levels, 'figs/height_obs.png')
pltTiles(mod, cmap, levels, 'figs/height_mod.png')
pltTiles(diff, dcmap, dlevels, 'figs/height_diff.png')
browser()
