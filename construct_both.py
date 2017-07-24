
fnameExt = ['VIS', 'NIR']


albIndex = [1,2]
tile_lev = [101 ,102  ,103  ,201  ,202  ,3    ,301  ,302  ,4    ,401  ,402  ,501  ,502  ,6      , 7    , 8         , 9    , 901, 902, 903, 904, 905, 906, 907, 908, 909, 910]
tile_nme = ['BD','TBE','tBE','NLD','NLE','C3G','C3C','C3P','C4G','C4C','C4P','SHD','SHE','Urban','Lake','Bare Soil','Ice', 'Ice1', 'Ice2', 'Ice3', 'Ice4', 'Ice5', 'Ice6', 'Ice7', 'Ice9', 'Ice9', 'Ice10']

alph_inf = [[0.1 ,0.1  ,0.1  ,0.07  ,0.07  ,0.1  ,0.09  ,0.09  ,0.1  ,0.106  ,0.106  ,0.1  ,0.1  ,0.18   ,0.06  , -1.0       , 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75],
    [0.45 ,0.45  ,0.45  ,0.35  ,0.35  ,0.58  ,0.365  ,0.365  ,0.58  ,0.337  ,0.377  ,0.58  ,0.58  ,0.18   ,0.06  , -1.0       , 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75]]
alph_k   = [[0.5 ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,None   ,None  ,None       ,None,None ,None ,None ,None ,None ,None ,None ,None ,None ,None  ],
    [0.5 ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,0.5  ,None   ,None  ,None       ,None,None ,None ,None ,None ,None ,None ,None ,None ,None ,None  ]]

alph_grp = [101, 101, 101, 201, 201, 3, 3, 3, 3, 3, 3, 501, 501, 6, 7, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,9]


prePlots = False
testOrderPlots = False

execfile("construct_albedo.py")
