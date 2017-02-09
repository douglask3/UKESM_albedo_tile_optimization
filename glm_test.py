from __future__ import print_function
import libs.import_iris
import iris
from libs import git_info
from libs.load_stash import *
from libs.listdir_path import *
import numpy as np
from   os    import listdir, getcwd, mkdir, path, walk
from   pylab import sort
from   pdb   import set_trace as browser

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import cartopy.crs as ccrs

import statsmodels.api as sm
from scipy import stats
from statsmodels.graphics.api import abline_plot
from statsmodels import graphics


##########################################################################
## cfg                                                                  ##
##########################################################################
data_dir = 'data/'

albedo_file = 'qrclim.land'
alb_sc_path = 'data/u-aj523/'
tile_f_file = 'JULES-ES.1p5.vn4.6.S3.dump.19900101.0.n96e_ORCA025.m01s00i216.anc'
albedo_index = 0

tile_lev = np.array([101  ,102       ,103       ,201  ,202  ,3    ,301  ,302  ,4    ,401  ,402  ,501  ,502  ,6      ,7     ,8          ,9    , 901  ,902   ,903   ,904   ,905   ,906   ,907   ,908   ,909   ,910])
tile_nme = np.array(['BLD','BLE_Trop','BLE_Temp','NLD','NLE','C3G','C3C','C3P','C4G','C4C','C4P','SHD','SHE','Urban','Lake','Bare Soil','Ice', 'Ice1','Ice2','Ice3','Ice4','Ice5','Ice6','Ice7','Ice8','Ice9','Ice10'])

albedo_n = ['SW', 'VIS', 'NIR']

##########################################################################
## Load data                                                            ##
##########################################################################
obs_alb = iris.load(data_dir + albedo_file)[1]
tile_f  = iris.load(data_dir + tile_f_file)[0]

## Load mod albedo scaling
mod_albi = load_stash(listdir_path(alb_sc_path), 'm01s01i271', 'VIS')


##########################################################################
## Construct required data                                              ##
##########################################################################
mod_alb = mod_albi[0][0].copy()

for lev in range(0,mod_albi.shape[0]):
    for t in range(0,obs_alb.shape[0]):
        mod_alb.data = mod_alb.data +  mod_albi[lev][t].data * tile_f[lev].data * obs_alb[t].data 

mod_alb = mod_alb / 12.0
obs_alb = obs_alb.collapsed('time', iris.analysis.MEAN)

##########################################################################
## Perform glm                                                          ##
##########################################################################
ncell = obs_alb.shape[0] * obs_alb.shape[1]
dep = obs_alb.data.reshape(ncell)


tot = tile_f.collapsed('pseudo_level', iris.analysis.SUM)
for i in range(0, tile_f.shape[0]): tile_f[i].data = tile_f[i].data / tot.data

ind = tile_f.data.reshape(17, ncell).transpose()
glm_norm = sm.GLM(dep, ind)
res = glm_norm.fit()

print(res.summary())
print('Parameters: ', res.params)
print('T-values: ', res.tvalues)


##########################################################################
## plot    glm                                                          ##
##########################################################################
nobs = res.nobs
y = dep
yhat = res.mu


ax = plt.subplot(321)
ax.scatter(yhat, y)
line_fit = sm.OLS(y, sm.add_constant(yhat, prepend=True)).fit()
abline_plot(model_results=line_fit, ax=ax)

ax.set_title('Model Fit Plot')
ax.set_ylabel('Observed values')
ax.set_xlabel('Fitted values');

ax = plt.subplot(322)

ax.scatter(yhat, res.resid_pearson)
ax.hlines(0, 0, 1)
ax.set_xlim(0, 1)
ax.set_title('Residual Dependence Plot')
ax.set_ylabel('Pearson Residuals')
ax.set_xlabel('Fitted values')

ax = plt.subplot(323)
resid = res.resid_deviance.copy()
resid_std = stats.zscore(resid)
ax.hist(resid_std, bins=25)
ax.set_title('Histogram of standardized deviance residuals');

git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
plt.gcf().text(.5, .05, git)
plt.savefig('figs/glm_construction.png', bbox_inches = 'tight')

graphics.gofplots.qqplot(resid, line='r')

git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
plt.gcf().text(.5, .05, git)
plt.savefig('figs/qqplot.png', bbox_inches = 'tight')

plt.close()
##########################################################################
## plot obs, mod, glm                                                   ##
##########################################################################
## Annual grid cel avarage
def plot_map(dat, plotN):
    plt.subplot(3, 2, plotN, projection=ccrs.Robinson())
    qplt.contourf(dat, levels =[0, 0.1, 0.15, 0.2, .25, 0.3], cmap = "brewer_Greys_09")
    plt.gca().coastlines()

def plot_cube(cube, N, M, n, levels = [0, 0.1, 0.15, 0.2, .25, 0.3], cmap = 'brewer_Greys_09'):
    plt.subplot(N, M, n, projection=ccrs.Robinson())

    cmap = plt.get_cmap(cmap)
    norm = BoundaryNorm(levels, ncolors=cmap.N - 1)

    qplt.contourf(cube,levels = levels,  cmap = cmap, norm = norm, extend = 'max')
    plt.gca().coastlines() 

glm_alb = obs_alb.copy()

glm_alb.data = res.predict().reshape(glm_alb.shape)
obs_alb.long_name = 'Observed'
mod_alb.long_name = 'Modelled'
glm_alb.long_name = 'Reconstructed'
plot_cube(obs_alb, 3, 2, 1)
plot_cube(mod_alb, 3, 2, 3)
plot_cube(glm_alb, 3, 2, 4)

plt.subplot(3, 2, 5)
plt.xlim(0.0, 1.0)
plt.ylim(0.0, 1.0)
plt.plot(obs_alb.data, mod_alb.data, 'ko')

plt.subplot(3, 2, 6)
plt.xlim(0.0, 1.0)
plt.ylim(0.0, 1.0)
plt.plot(obs_alb.data, glm_alb.data, 'ko')


git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
plt.gcf().text(.5, .8, git)
plt.savefig('figs/albedo_recon_comparison_.png', bbox_inches = 'tight')



tile_n = tile_f.coord('pseudo_level').points
tile_n = [tile_nme[tile_lev == i][0] for i in tile_f.coord('pseudo_level').points]

