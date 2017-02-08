import iris
from libs import git_info
import numpy as np
from   os    import listdir, getcwd, mkdir, path, walk
from   pylab import sort
from   pdb   import set_trace as browser

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

data_dir = 'data/'

albedo_file = 'qrclim.land'
tile_f_file = 'JULES-ES.1p5.vn4.6.S3.dump.19900101.0.n96e_ORCA025.m01s00i216.anc'
albedo_index = 0

tile_lev = np.array([101  ,102       ,103       ,201  ,202  ,3    ,301  ,302  ,4    ,401  ,402  ,501  ,502  ,6      ,7     ,8          ,9    , 901  ,902   ,903   ,904   ,905   ,906   ,907   ,908   ,909   ,910])
tile_nme = np.array(['BLD','BLE_Trop','BLE_Temp','NLD','NLE','C3G','C3C','C3P','C4G','C4C','C4P','SHD','SHE','Urban','Lake','Bare Soil','Ice', 'Ice1','Ice2','Ice3','Ice4','Ice5','Ice6','Ice7','Ice8','Ice9','Ice10'])

albedo_n = ['243', '244', '245']

## Load data
albedos = iris.load(data_dir + albedo_file)
tile_f  = iris.load(data_dir + tile_f_file)[0]

tile_n = tile_f.coord('pseudo_level').points
tile_n = [tile_nme[tile_lev == i][0] for i in tile_f.coord('pseudo_level').points]

for i in range(0, len(albedos)):
    albedo = albedos[i].collapsed('time', iris.analysis.MEAN)

    plt.figure(figsize = (15, 15))
    for tile in range(0, tile_f.shape[0]):
        plt.subplot(5,4,tile)
        plt.plot(tile_f[tile].data[:], albedo.data[:], "ko")
        plt.grid(True)
        plt.title(tile_n[tile])

    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.35,
                        wspace=0.25)
    git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
    plt.gcf().text(.05, .05, git)
    
    fname = 'figs/albedo_' + albedo_n[i] +'.png'
    plt.savefig(fname, bbox_inches = 'tight')


