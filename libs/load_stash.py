import iris
from   pdb import set_trace as browser
from   pylab import sort 
from   libs.ExtractLocation import *
from   libs.listdir_path import *

def load_stash(files, code, name, units = None):
    print name
    print code

    stash_constraint = iris.AttributeConstraint(STASH = code)
    
    cube = iris.load_cube(files, stash_constraint)
    cube.var_name = name
    cube.standard_name = None
    if (units is not None): cube.units = units
    return cube   

def loadCube(dir, *args, **kw):
    files = sort(listdir_path(data_dir + dir))
    files = files[0:120]
    dat = iris.load_cube(files)
    
    dat = ExtractLocation(dat, *args, **kw).cubes

    dat.data = (dat.data > 0.00001) / 1.0
    return dat 
