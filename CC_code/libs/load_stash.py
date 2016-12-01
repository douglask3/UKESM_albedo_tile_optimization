import iris
from pdb import set_trace as browser

def load_stash(files, code, name, units = None):
    print name
    print code

    stash_constraint = iris.AttributeConstraint(STASH = code)
    
    cube = iris.load_cube(files, stash_constraint)
    cube.var_name = name
    cube.standard_name = None
    if (units is not None): cube.units = units
    return cube    
