import iris

def load_stash(files, code, name):
    stash_constraint = iris.AttributeConstraint(STASH = code)
    cube = iris.load_cube(files, stash_constraint)
    cube.long_name = name
    return cube    
