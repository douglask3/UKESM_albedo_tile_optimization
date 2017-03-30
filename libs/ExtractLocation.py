import iris

class ExtractLocation(object):
    def __init__(self, cubes, east, west, south, north):
        self.lon = self.coordRange2List([east, west])
        self.lat = self.coordRange2List([south, north])
    
        def lonRange(cell): return self.lon[0] <= cell <= self.lon[1]
        def latRange(cell): return self.lat[0] <= cell <= self.lat[1]

        if self.lon is not None:
            try:
                cubes = cubes.extract(iris.Constraint(longitude = lonRange))
            except:
                cubes = [cube.extract(iris.Constraint(longitude = lonRange)) for cube in cubes]
        if self.lat is not None:
            try:
                cubes = cubes.extract(iris.Constraint(latitude  = latRange))
            except:
                cubes = [cube.extract(iris.Constraint(latitude  = latRange)) for cube in cubes]
        self.cubes = cubes

    def coordRange2List(self, c):
        if c is not None:
            if not isinstance(c, list) or len(c) == 1: c = [c, c]
            if c[0] is None: return None
        return c

