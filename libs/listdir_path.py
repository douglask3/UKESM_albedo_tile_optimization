from   os    import listdir

def listdir_path(path):    
    files = listdir(path)
    files = [path + i for i in files]
    return files
