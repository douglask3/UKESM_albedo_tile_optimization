#############################################################################
## cfg                                                                     ##
#############################################################################
import numpy as np
## General
data_dir = 'data/'
mods_dir = ['u-ak508/', 'u-ak518/']
running_mean = False

## albedo
fign    = 'snowDays'
ttle    = 'Snow_Days'
unit    = '%'
levels  = np.arange(0, 35, 5)
dlevels = np.array([0.1, 1, 3, 5, 10])
dlevels = np.concatenate([ -dlevels[::-1], dlevels])
cmap    = 'brewer_GnBu_09'
dcmap   = 'brewer_Spectral_11'


#############################################################################
## libs                                                                    ##
#############################################################################

import libs.import_iris #comment out this line if not run on CEH linux box
import iris

from   pylab import sort      
import matplotlib.pyplot as plt

from   libs              import git_info
from   libs.plot_maps    import *
from   libs.plot_TS      import *
from   libs.listdir_path import *
from   libs.load_stash   import *

from   pdb   import set_trace as browser  

#############################################################################
## Funs                                                                    ##
#############################################################################


def snowInJob(dir):
    files = sort(listdir_path(data_dir + dir))
    files = files[0:60]
    
    dat = iris.load_cube(files)
    dclim = dat[0:360].copy()
    mclim = dat[15:360:30].copy()

    dat.data = dat.data > 0.00001

    ## convert to climatology
    nyrs = np.floor(dat.shape[0] / 360.0)

    for day in range(0, 360):
        dclim.data[day] = dat[day::360].collapsed('time', iris.analysis.SUM).data / nyrs

    pp = -1
    for mn in range(0, 12):
        md = mn * 30
        mclim.data[mn] = dclim[md:(md+30)].collapsed('time', iris.analysis.SUM).data
        mclim.units = 'day'


    ##########################
    ## Plot                 ##
    ##########################
    plot_cubes_map(mclim, 'JFMAMJJASOND', cmap, levels, nx = 6, ny = 3)
    
    plt.subplot(4, 1, 4)
    plot_cube_TS([mclim], False)
    
    fig_name = 'figs/' + fign + dir[:-1] + '.pdf'
    plt.savefig(fig_name)
    return(mclim)


snowDays = [snowInJob(dir) for dir in mods_dir]
diff = snowDays[0].copy()
diff.data = snowDays[1].data - snowDays[0].data
#for i in range(0,12): diff[i].data = snowDays[1][i].data - snowDays[0][i].data

plot_cubes_map(diff, 'JFMAMJJASOND', dcmap, dlevels, extend = 'both', nx = 6, ny = 3)
    
plt.subplot(4, 1, 4)
plot_cube_TS(snowDays, False)

fig_name = 'figs/' + fign + 'diff' + '.pdf'
plt.savefig(fig_name)


