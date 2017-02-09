from __future__ import print_function

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

import statsmodels.api as sm
from scipy import stats
from statsmodels.graphics.api import abline_plot
from statsmodels import graphics

data_dir = 'data/'

albedo_file = 'qrclim.land'
tile_f_file = 'JULES-ES.1p5.vn4.6.S3.dump.19900101.0.n96e_ORCA025.m01s00i216.anc'
albedo_index = 0

tile_lev = np.array([101  ,102       ,103       ,201  ,202  ,3    ,301  ,302  ,4    ,401  ,402  ,501  ,502  ,6      ,7     ,8          ,9    , 901  ,902   ,903   ,904   ,905   ,906   ,907   ,908   ,909   ,910])
tile_nme = np.array(['BLD','BLE_Trop','BLE_Temp','NLD','NLE','C3G','C3C','C3P','C4G','C4C','C4P','SHD','SHE','Urban','Lake','Bare Soil','Ice', 'Ice1','Ice2','Ice3','Ice4','Ice5','Ice6','Ice7','Ice8','Ice9','Ice10'])

albedo_n = ['SW', 'VIS', 'NIR']

## Load data
albedos = iris.load(data_dir + albedo_file)[0]
tile_f  = iris.load(data_dir + tile_f_file)[0]


albedo = albedos.collapsed('time', iris.analysis.MEAN)

ncell = albedo.shape[0] * albedo.shape[1]
dep = albedo.data.reshape(ncell)
ind = tile_f.data.reshape(17, ncell).transpose()


glm_norm = sm.GLM(dep, ind)

res = glm_norm.fit()
print(res.summary())


print('Parameters: ', res.params)
print('T-values: ', res.tvalues)



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


#ax = plt.subplot(324)
#ax.graphics.gofplots.qqplot(resid, line='r')

## Annual grid cel avarage
def plot_map(dat, plotN):
    plt.subplot(3, 2, plotN, projection=ccrs.Robinson())
    qplt.contourf(dat, levels =[0, 0.1, 0.15, 0.2, .25, 0.3], cmap = "brewer_Greys_09")
    plt.gca().coastlines()


mod = albedo.copy()
obs = albedo.copy()
mod.data = res.predict().reshape(mod.shape)
obs.long_name = 'Observed'
mod.long_name = 'Reconstructed'
plot_map(obs, 5)
plot_map(mod, 6)

plt.show()
browser()


tile_n = tile_f.coord('pseudo_level').points
tile_n = [tile_nme[tile_lev == i][0] for i in tile_f.coord('pseudo_level').points]

for i in range(0, len(albedos)):
    albedo = albedos[i]#.collapsed('time', iris.analysis.MEAN)
    

    plt.figure(figsize = (15, 15))
    for tile in range(0, tile_f.shape[0]):
        plt.subplot(5,4,tile +1)
        plt.xlim(0.0, 1.0)
        plt.ylim(0.0, 1.0)
        
        for month in range(0,albedo.shape[0]):
            plt.plot(tile_f[tile].data[:], albedo[month].data[:], "ko")

        plt.grid(True)
        plt.text(0.5, 0.87, tile_n[tile],
                 horizontalalignment = 'center', fontsize = 20)

        if (tile / 4 !=  tile / 4.0): plt.tick_params(labelleft   = 'off')
        if ((tile + 1) / 4 ==  (tile + 1) / 4.0): plt.tick_params(labelright   = 'on')

        if (tile < 4): plt.tick_params(labeltop   = 'on')
        if (tile < (17 - 4)):  plt.tick_params(labelbottom = 'off')
    
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.07,
                        wspace=0.09)
    git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
    plt.gcf().text(.5, .05, git)

    
    plt.gcf().text(.06, .5, albedo_n[i] + ' albedo', rotation = 90,
                   verticalalignment = 'center', fontsize = 18)
    
    plt.gcf().text(.5, .22, 'tile fractional cover',
                   horizontalalignment = 'center', fontsize = 18)
    fname = 'figs/albedo_' + albedo_n[i] +'.png'
    plt.savefig(fname, bbox_inches = 'tight')
    


