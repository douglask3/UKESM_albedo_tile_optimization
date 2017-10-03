import libs.import_iris
import iris
import iris.coords
import numpy as np

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from scipy.optimize import minimize


def splitOptimizationParams(params):
    a_wl = params[:npft]
    a_ws = params[npft:(2*npft)]
    b_wl = params[(2*npft):]
    return a_wl, b_wl, a_ws
    
def woodC(LAI_b, a_wl, b_wl):
    return a_wl * LAI_b ** b_wl
    
def height(LAI_b, a_wl, b_wl, a_ws = 1.0, eta_sl = 0.01):
    W = woodC(LAI_b, a_wl, b_wl)
    return W / (a_ws * eta_sl) * ((a_wl / W)** (1/b_wl))
    

def minFun(params):

    a_wl, b_wl, a_ws  = splitOptimizationParams(params)
    
    h = height(LAI_b.data, a_wl, b_wl, a_ws)    
    
    return h.mean()

start = #from u-aq226
bounds = [np.repeat((0.001, 1), npft), np.repeat((1.1, 2.0), npft), np.repeat((1, 20), npft)]
res = minimize(minFun, start, bounds = bounds, method='SLSQP',  options={'xtol': 1e-3, 'disp': True}).x

h = height(LAI_b.data, a_wl, b_wl)

plt.subplot(2,2,1)
plt.scatter(LAI_b.data, h0)

plt.subplot(2,2,2)
plt.scatter(LAI_b.data, h)

plt.subplot(2,2,3)
qplt.contourf(hcube)

plt.subplot(2,2,3)
qplt.contourf(hcube - hocubegit)
