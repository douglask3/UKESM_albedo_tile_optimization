#############################################################################
## cfg                                                                     ##
#############################################################################
import numpy as np
## General
data_dir = 'data/'
mods_dir = ['u-ak508/', 'u-ak518/']
running_mean = False

## albedo
fign = 'snowDays'
ttle = 'Snow_Days'
unit = '%'
levels = range(0, 35, 5)
cmap = 'brewer_GnBu_09'


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

for dir in mods_dir:
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
    fig_name = 'figs/' + fign + dir[:-1] + '.pdf'
    #git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev

    
    plot_cubes_map(mclim, 'JASONDJFMAMJ', cmap, levels, nx = 6, ny = 3)
    
    plt.subplot(4, 1, 4)
    plot_cube_TS([mclim], False)
    
    #plt.gcf().text(.05, .95, git, rotation = 90)
    plt.savefig(fig_name)

