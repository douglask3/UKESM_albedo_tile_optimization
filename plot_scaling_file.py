import iris
import numpy as np
from   os    import listdir, getcwd, mkdir, path, walk
from   pylab import sort
from   pdb   import set_trace as browser

data_dir = 'data/'
mod_out = 'ag589/'
stash_code = 'm01s00i216'

def listdir_path(path):
    from os import listdir
    
    files = listdir(path)
    files = [path + i for i in files]
    return files


mod_files = sort(listdir_path(data_dir + mod_out))
stash_contraint = iris.AttributeConstraint(STASH = stash_code)

cube = iris.load_cube(mod_files, stash_contraint)

browser()
