import numpy as np
import iris
from   pdb               import set_trace as browser

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from   libs.ExtractLocation import *

from scipy.optimize import minimize
from   pdb               import set_trace as browser

class Albedo(object):
    def __init__(self, frac, lai, alpha_0, alpha_inf, k):
        self.frac = frac
        self.lai  = lai
        self.alpha_inf = alpha_inf 
        self.alpha_0 = alpha_0    
        self.k = k 

        self.frac_has_time = len(which_coord(self.frac, 'time')) > 0
    
    def tile(self, tile, alpha_inf = None, k = None):
        
        lai = self.extraPseudo_level(self.lai, tile)
        
        if k         is None: k         = self.k[tile]
        if alpha_inf is None: alpha_inf = self.alpha_inf[tile]
        
        tile0 = self.lai.coord('pseudo_level').points[0]
        alpha = self.extraPseudo_level(self.lai, tile0).copy()
        alpha.coord('pseudo_level').points[0] = tile
        alpha.attributes = None
        
        if lai is None:            
            alpha.data[:,:,:] = self.alpha_0.data if alpha_inf < 0.0 else alpha_inf   
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
        
    def tiles(self, annual = True, alpha_inf = None, k = None):
        if alpha_inf is None: 
            alphas =  [self.tile(tile) for tile in self.frac.coord('pseudo_level').points]
        else:
            alphas =  [self.tile(tile, aInf, k) for tile, aInf, k in zip(self.frac.coord('pseudo_level').points, alpha_inf, k)]
        ## switch alphas time and frac dimensions round
        alphas = iris.cube.CubeList(alphas).merge_cube()
        
        if annual: alphas = alphas.collapsed('time', iris.analysis.MEAN)
        return alphas

    def cell(self, annual = False, *arg, **kw):
        alphas = self.tiles(annual, *arg, **kw)
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

    def Initials(self, x, index = None):
            if index is None: index = self.frac.coord('pseudo_level').points
            return [x[i] for i in index]

    def optimize(self, observed, para_index, *args, **kw):
        ##########################
        ## prepare obs          ##
        ##########################
        coords = ('longitude', 'latitude') ## Unhardcode
        try: 
            observed.coord('latitude').guess_bounds()
        except:
            pass
        try: 
            observed.coord('longitude').guess_bounds()
        except:
            pass

        self.observed = observed

        ##########################
        ## prepare initals      ##
        ##########################
        
        para_index0 = para_index
        para_index = self.Initials(para_index)
        indicies   = np.unique(para_index)
        self.indexInverse = [np.where(indicies == i)[0][0] for i in para_index]

        start_inf  = self.Initials(self.alpha_inf, index = indicies)
        bounds_inf = [(0.0, 1.0) if i >= 0.0 else (-1.0, -1.0) for i in start_inf]
    
        start_k   = self.Initials(self.k        , index = indicies)
        start_k   = [-1 if i is None else i for i in start_k]
        bounds_k  = [(0.0, 10.0) if i >= 0.0 else (-1.0, -1.0) for i in start_inf]

        start = start_inf + start_k
        bounds = bounds_inf + bounds_k

        self.phalf = len(start)/2
        
        observed = ExtractLocation(observed, *args, **kw).cubes
        grid_areas = iris.analysis.cartography.area_weights(observed)
 
        def minFun(params):
           
            aInf = params[:self.phalf]
            aK   = params[self.phalf:]
            aK = [None if i < 0 else i for i in aK]

            print('----')
            print(aInf)
            print(aK)
            
            alpha_inf = self.Initials(aInf, self.indexInverse)
            k         = self.Initials(aK  , self.indexInverse)
            
            modelled = self.cell(annual = False, alpha_inf = alpha_inf, k = k)
            modelled.data[modelled.data < 0.0] = 0.0
            
            diff = self.observed.copy()
            diff.data = abs(modelled.data - self.observed.data)
            
            diff = ExtractLocation(diff, *args, **kw).cubes
            diff.data = np.nan_to_num(diff.data) 

            collapsed_cube = diff.collapsed(coords,iris.analysis.MEAN,weights=grid_areas)
            modelled.data = np.nan_to_num(modelled.data)    
            diff = collapsed_cube.data.sum()
            print(diff)
            return collapsed_cube.data.sum()
        
 
        
        #res = minimize(minFun, start, bounds = bounds, method='SLSQP',  options={'maxiter': 5, 'xtol': 1e-1, 'disp': True}).x
        res = [i + 0.1 for i in start]
        
        alpha_inf = self.Initials(res[:self.phalf], self.indexInverse)
        k         = self.Initials(res[self.phalf:], self.indexInverse)
        self.k   = [None if i < 0 else i for i in self.k]   

        tileID = self.frac.coord('pseudo_level').points
        self.alpha_inf = dict(zip( tileID, alpha_inf))
        self.k         = dict(zip( tileID, k))     

        return self.alpha_inf, self.k


def coord_names(cube):
    return [coord.name() for coord in cube.coords()]

def which_coord(cube, nm):
    return np.where([coord.name() == nm for coord in cube.coords()])[0]


    
