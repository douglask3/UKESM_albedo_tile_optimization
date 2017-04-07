import numpy as np
import iris
from   pdb               import set_trace as browser

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt

class Albedo(object):
    def __init__(self, frac, lai, alpha_0, alpha_inf, k):
        self.frac = frac
        self.lai  = lai
        self.alpha_inf = alpha_inf 
        self.alpha_0 = alpha_0    
        self.k = k 

        self.frac_has_time = len(which_coord(self.frac, 'time')) > 0
    
    def tile(self, tile):
        
        lai = self.extraPseudo_level(self.lai, tile)
        print(tile)
        k   = self.k[tile]
        alpha_inf = self.alpha_inf[tile]
        
        tile0 = self.lai.coord('pseudo_level').points[0]
        alpha = self.extraPseudo_level(self.lai, tile0).copy()
        alpha.coord('pseudo_level').points[0] = tile
        alpha.attributes = None

        if lai is None:            
            alpha.data[:,:,:] = self.alpha_0.data if alpha_inf == -1.0 else alpha_inf   
        else:
            F = alpha.copy()
            F.data[:,:] = 1.0 if k is None else 1.0 - np.exp(-k * lai.data)
            F = F * alpha_inf + (F * (-1) + 1) * self.alpha_0
            alpha.data.data[:] = F.data.data[:]
        
        for i in range(0, alpha.shape[0]):
            alpha.data[i][self.alpha_0.data.mask] = None
        alpha.standard_name = None
        alpha.varn_name = 'albedo'
        return alpha
        
    def tiles(self, annual = True):
        alphas =  [self.tile(i) for i in self.frac.coord('pseudo_level').points]
        ## switch alphas time and frac dimensions round
        alphas = iris.cube.CubeList(alphas).merge_cube()
        
        if annual: alphas = alphas.collapsed('time', iris.analysis.MEAN)
        return alphas

    def cell(self, annual = False):
        alphas = self.tiles(annual)
        if annual:
            frac = self.frac.collapsed('time', iris.analysis.MEAN)  \
                if self.frac_has_time else self.frac
            alphas = alphas * frac
        else:
            if self.frac_has_time:
                alphas.data *= self.frac.data
            else:                
                for tile in range(alphas.shape[1]):                   
                    alphas.data[:,tile,:] = alphas.data[:,tile,:] * self.frac.data
 

        return alphas.collapsed('pseudo_level', iris.analysis.SUM)

    def extraPseudo_level(self, cube, x):
        return cube.extract(iris.Constraint(pseudo_level = x))


def coord_names(cube):
    return [coord.name() for coord in cube.coords()]

def which_coord(cube, nm):
    return np.where([coord.name() == nm for coord in cube.coords()])[0]
