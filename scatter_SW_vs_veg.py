import iris
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

jobIDs = ['u-ak518', 'u-al888', 'u-al889', 'u-al890', 'u-al891', 'u-am152']
pltFrs = [True     , False    , False    , False    , False    , False    ]
# Define paths and parameters
gc3p1_frac_file = '../UKESM_veg_redistribution/data/qrparm.veg.frac'
ukesm_frac_file = 'data/' + 'u-ak518' +'/' + 'u-ak518' +'/'

gc3p1__SW__file = 'u-ak508/SW/'

SWd__code = 'm01s01i210'
SWu__code = 'm01s01i211'

mapFigFile = "albedoClim"
mapFigFileFrac = "fracCover"
fig_file   = "figs/fracChangeVsAlbedo.png"

tile_9names  = ['BL', 'NL', 'C3', 'C4', 'Shrub', 'Urban', 'Water', 'Soil', 'Ice']
pft_27_2_9   = [  3,   4,   6,   7,   8,   9, 1, 1, 1, 2, 2, 3, 3,
       4, 4, 5, 5, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9] 

albedoLevels  = [0,  0.1, 0.2, 0.3, 0.4, 0.6, 0.8]
dalbedoLevels = [-1, -0.5, -0.2, -0.1, -0.05, 0.05, 0.1, 0.2, 0.5, 1]

###############################################
## Load mask and remove coordinate system    ##
###############################################
git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev

pxs = [3, 6, 7]
pys = [4, 4, 5]
def pltJob(jobID, pltFrc):
    ukesm__SW__file = jobID +'/SW/'
    gc3p1_albd = plotSWoverSW(gc3p1__SW__file, mapFigFile + 'gcsp1',
                              jobID = 'u-ak508', levels = albedoLevels)

    ukesm_albd = plotSWoverSW(ukesm__SW__file, mapFigFile + 'uksem', jobID = jobID, 
                              levels = albedoLevels)
    if (pltFrc):
        gc3p1_frac = iris.load_cube(gc3p1_frac_file)
        ukesm_frac = load_stash_dir(ukesm_frac_file, 'm01s19i013')
        ukesm_frac = ukesm_frac.collapsed('time', iris.analysis.MEAN)

        ukesm_groups = ukesm_frac[0:9].copy()
        ukesm_groups.data[:]= 0.0
    
        for i in range(1,10):
            index = np.where(np.array(pft_27_2_9) == i)
            for j in index[0]: ukesm_groups.data[i - 1] += ukesm_frac.data[j]

        diff_frac = ukesm_groups.copy()
        diff_frac.data -= gc3p1_frac.data

        plotAllRegions(diff_frac, mapFigFileFrac + 'uksem-gc3p1', jobID = jobID +'-ak508',
                       levels = dalbedoLevels, cmap = 'brewer_PiYG_11', nms = tile_9names,
                       tsYlim = [-0.25, 0.05] )

    diff_albd = ukesm_albd[0:30].copy()
    diff_albd.data -= gc3p1_albd.data[0:30]

    plotAllRegions(diff_albd, mapFigFile + 'uksem-gc3p1', jobID = jobID +'-ak508',
                  levels = dalbedoLevels, cmap = 'brewer_Spectral_11',
                       tsYlim = [-0.25, 0.05])
    if not pltFrc: return diff_albd
    diff_albd = convert2Climatology(diff_albd, mnthLength = 1)
    diff_frac.coord('latitude' ).guess_bounds()
    diff_frac.coord('longitude').guess_bounds()

    xplot = 4#diff_albd.shape[0]
    yplot = 4#diff_frac.shape[0]

    def plot_Month_scatter(alb, frc, m, f, nplot, frac_lab, albd_lab):
        plt.subplot(xplot, yplot, nplot)
        xd = frc[f].data.flatten()
        yd = alb[m].data.flatten()

        try:
            mask = np.invert(xd.mask)
            xd = xd[mask]
            yd = yd[mask]
        except:
            pass
    
        mask = np.invert(np.isnan(xd + yd))
    
        xd = xd[mask]
        yd = yd[mask]
    
        # sort the data
        reorder = xd.argsort()
        xd = xd[reorder]
        yd = yd[reorder]

        plt.scatter(xd, yd, s=30, alpha=0.15, marker='o')   

        try:
            par = np.polyfit(xd, yd, 1, full=True)

            slope = par[0][0]
            intercept = par[0][1]
            xl = [min(xd), max(xd)]
            yl = [slope*xx + intercept  for xx in xl]

            # coefficient of determination, plot text
            variance = np.var(yd)
            residuals = np.var([(slope*xx + intercept - yy)  for xx,yy in zip(xd,yd)])
            Rsqr = np.round(1-residuals/variance, decimals=2)
            plt.text(.6*max(xd)+.4*min(xd),.9*max(yd)+.1*min(yd),
                     '$R^2 = %0.2f$'% Rsqr, fontsize=20)

            plt.xlabel(frac_lab)
            plt.ylabel(albd_lab)

            # error bounds
            yerr = [abs(slope*xx + intercept - yy)  for xx,yy in zip(xd,yd)]
            par = np.polyfit(xd, yerr, 2, full=True)

            yerrUpper = [(xx*slope+intercept)+(par[0][0]*xx**2 + par[0][1]*xx + par[0][2]) for xx,yy in zip(xd,yd)]
            yerrLower = [(xx*slope+intercept)-(par[0][0]*xx**2 + par[0][1]*xx + par[0][2]) for xx,yy in zip(xd,yd)]

            plt.plot(xl, yl, '-r')
            plt.plot(xd, yerrLower, '--r')
            plt.plot(xd, yerrUpper, '--r')
        except:
            pass
    
    def PlotRegion(rname, *args, **kw):
        alb = ExtractLocation(diff_albd, *args, **kw).cubes
        frc = ExtractLocation(diff_frac, *args, **kw).cubes
    
        if frc.shape[1] != alb.shape[1]: browser()
    
        plt.figure(figsize = (16, 16))
        nplot = 0
        for i in [11,0,1,2]:
            for j in [1, 2, 4, 7]:
                nplot = nplot + 1
                xlab = tile_9names[j] if i == 2  else ""
                ylab = 'JFMAMJJASOND'[i] if j == 1 else ""
                plot_Month_scatter(alb, frc, i, j, nplot, xlab, ylab)
    
        git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
        plt.gcf().text(.18, .05, git, fontsize = 8)
    
        plt.suptitle(rname, fontsize = 30)
        savefig('figs/gc3p1_to_ukesm05_albedo_frac-' + jobID + rname + '.png')


    for r, e, w, s, n in zip(regionNames, east, west, south, north):
        PlotRegion(r, east = e, west = w, south = s, north = n)

[pltJob(jobID, pltFrc) for jobID, pltFrc in zip(jobIDs, pltFrs)]
