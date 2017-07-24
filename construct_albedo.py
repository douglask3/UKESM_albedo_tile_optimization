import libs.import_iris
import iris
import iris.coords
import numpy as np

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

import csv

from   os                import listdir, getcwd, mkdir, path, walk
from   pylab             import sort
from   pdb               import set_trace as browser

from   libs              import git_info
from   libs.listdir_path import *
from   libs.weightedFuns import *
from   libs.which        import *
from   libs.nanRound     import *
from   libs.grid_area    import grid_area
from   libs.Albedo       import Albedo

from   libs.plot_maps    import *

###############################################
## Setup                                     ##
###############################################
Albe_file = 'data/qrclim.land'
Frac_file = 'data/qrparm_frac_27_tile_orca1_cci.anc'
LAI__file = 'data/qrparm_func_orca1_13_tile.anc'
slAb_file = 'data/qrparm.soil'
slAb_varn = 'soil_albedo'

albedoLevels  = [0,  0.1, 0.2, 0.3, 0.4, 0.6, 0.8]
dalbedoLevels = [-0.5, -0.2, -0.1, -0.05, -0.01, 0.01, 0.05, 0.1, 0.2, 0.5]
monthNames = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
              'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

###############################################
## Open data                                 ##
###############################################
frac    = iris.load_cube(Frac_file)
tileIndex = frac.coords('pseudo_level')[0].points
lais    = iris.load(LAI__file)[1]
soilAlb = iris.load_cube(slAb_file, slAb_varn)


observed = [iris.load(Albe_file)[i] for i in albIndex]
mxLAI   = lais.collapsed('time', iris.analysis.MAX)

###############################################
## Indexing                                  ##
###############################################
tileIndex = frac.coords('pseudo_level')[0].points
PlotOrder = [which(tileIndex, i)[0] for i in tile_lev ]
ParaOrder = [which(tile_lev,  i)[0] for i in tileIndex]

def reOrder(lst, idx):  
    lst = [[l[i] for i in idx] for l in lst]
    return lst

alph_infIndex = reOrder(alph_inf, ParaOrder)
alph_kIndex   = reOrder(alph_k  , ParaOrder)

###############################################
## Basic plotting                            ##
###############################################
def plot_cubes_map_ordered(cube, *args, **kw):
    codes = [frac.coords('pseudo_level')[0].points[i] for i in PlotOrder]
    cube = [cube[i] for i in PlotOrder if i < cube.shape[0]]
    nms = [i + '-' + str(j) for i,j in zip(tile_nme, codes)]
    plot_cubes_map(cube, nms, figXscale = 4, *args, **kw)


if prePlots:
    plot_cubes_map_ordered(frac, 'brewer_Greens_09',
                           [0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5], 'max',
                          'figs/N96e_GA7_17_tile_cci_reorder.png',
                          'fractional cover')

    plot_cubes_map_ordered(mxLAI, 'brewer_Greens_09',
                           [0, 0.1, 0.2, 0.5, 1, 2, 5], 'max',
                           'figs/N96e_GA7_qrparm.veg.13.pft.217.func.annualMax.png',
                           'LAI')
    if testOrderPlots:
        for mn in range(0,12):
            plot_cubes_map_ordered(lais[:, mn, :, :], 'brewer_Greens_09',
                                   [0, 0.1, 0.2, 0.5, 1, 2, 5], 'max',
                                   'figs/N96e_GA7_qrparm.veg.13.pft.217.func' + 'month' + str(mn) + '.png',
                                   'LAI')
    
        for pft in range(0, 13):
            npft = lais.coord('pseudo_level').points[pft]
            npft = tile_nme[np.where(tile_lev == npft)[0]] + '-' + str(npft)
            plot_cubes_map(lais[pft], monthNames, 'brewer_Greens_09',
                           [0, 0.1, 0.2, 0.5, 1, 2, 5], 'max',
                          'figs/N96e_GA7_qrparm.veg.13.pft.217.func' + 'tile' + npft + '.png',
                          'LAI', figXscale = 4)

###############################################
## Albedo construction                       ##
###############################################
def dictZip(index, lst):
    return  [dict(zip(index, i)) for i in lst]

alph_inf = dictZip(tile_lev, alph_inf)
alph_k   = dictZip(tile_lev, alph_k  )

albedo = Albedo(frac, lais, soilAlb,  alph_inf, alph_k)

aConstructed = albedo.cell(True)
mConstructed = albedo.cell()

###############################################
## Basic Albedo plots                        ##
###############################################
## tile albedo
def plotAlbedoByTiles(alb, name):
    Talb = alb.tiles()
    for i in range(len(Talb)):
        plot_cubes_map_ordered(Talb[i], 'pink',
                           albedoLevels, 'max',
                          'figs/' + name + '_tile_albedos-' + fnameExt + '-' + str(i) + '.png',
                          'albedo')
        
#plotAlbedoByTiles(albedo, 'constructed')
 
    
###############################################
## Optimize albedo                           ##
###############################################

optimized_alpha_inf, optimized_k = albedo.optimize(observed,
                                        dict(zip(tile_lev, alph_grp)),
                                         north = 60, south = -90)

albedoOptimized = Albedo(frac, lais, soilAlb, optimized_alpha_inf, optimized_k)


aOptimized = albedoOptimized.cell(True)
mOptimized = albedoOptimized.cell()
###############################################
## Plot annual optimized                     ##
###############################################

def plotAnnual(obs, aCon, aOpt, name):
    aObs = obs.collapsed('time', iris.analysis.MEAN)

    aCon.units = obs.units
    aOpt.units = obs.units


    plot_cubes_map([aCon, aOpt, aObs], ['constructed', 'optimized', 'observed'], 
                  'pink',  albedoLevels, 'max',
                  'figs/compare_albedos-' + name + '.png',  'albedo', figXscale = 8)

    dCon = aCon.copy()
    dCon.data -= aObs.data

    dOptCon = aOpt.copy()
    dOptObs = aOpt.copy()
    dOptCon.data -= aCon.data
    dOptObs.data -= aObs.data
    plot_cubes_map([dCon, dOptCon, dOptObs], 
                  ['constructed - observed', 'optimized - constructed', 'optimized - obsvered'],
                  'brewer_RdYlGn_11',  dalbedoLevels, 'both', 
                  'figs/compare_albedos_diff-' + name + '.png',  'albedo', figXscale = 8)

###############################################
## Plot Monthly optimized                     ##
###############################################
def plotMonthly(obs, mCon, mOpt, name):
    plot_cubes_map(mCon, monthNames, 'pink',
                   albedoLevels, 'max',
                  'figs/constructed_monthly_albedos-' + name + '.png',
                  'albedo', figXscale = 4)


    plot_cubes_map(mOpt, monthNames, 'pink',
                 albedoLevels, 'max',
                'figs/optimized_monthly_albedos-' + name + '.png',
                 'albedo', figXscale = 4)

    mOptObs = mOpt.copy()
    mOptObs.data -= obs.data

    plot_cubes_map(mOptObs, monthNames, 'brewer_RdYlGn_11',
                  dalbedoLevels, 'both',
                  'figs/optimized_monthly_albedos_vs_Obs-' + name + '.png',
                  'albedo', figXscale = 4)

    mOptCon = mOpt.copy()
    mOptCon.data -= mOpt.data
    plot_cubes_map(mOptCon, monthNames, 'brewer_RdYlGn_11',
                  dalbedoLevels, 'both',
                  'figs/optimized_monthly_albedos_vs_Cons-' + name + '.png',
               'albedo', figXscale = 4)

def outputParams(prior, post, name):
    params = [[i, prior[i], post[i]] for i in tile_lev]
    params.insert(0, ['tile', 'prior', 'post'])

    with open('outputs/' + name + '-.csv', "wb") as f:
        writer = csv.writer(f)
        writer.writerows(params)

for i in range(len(observed)):
    plotAnnual (observed[i], aConstructed[i], aOptimized[i], fnameExt[i])
    plotMonthly(observed[i], mConstructed[i], mOptimized[i], fnameExt[i])

    outputParams(alph_inf[i], optimized_alpha_inf[i], 'alpha_inf-' +  fnameExt[i])
    outputParams(alph_k[i]  , optimized_k[i]        , 'alpha_k-'   +  fnameExt[i])

browser()
#plotAlbedoByTiles(albedo, 'optimized')








