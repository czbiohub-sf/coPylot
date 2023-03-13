import sys
import os
sys.path.append(os.path.join(os.pardir, os.pardir, os.pardir))
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from widgets.scan_algrthm.scan_algorithm import ScanAlgorithm
from widgets.utils.affinetransform import AffineTransform
mpl.rcParams['agg.path.chunksize'] = 20000

#%%
initial_coord = (549.5, 754.5)
size = (300, 300)
gap = 10
shape = 'square'
sec_per_cycle = 0.003
sg = ScanAlgorithm(initial_coord, size, gap, shape, sec_per_cycle)

# coord = sg.generate_cornerline()
# coord = sg.generate_lissajous()
coord = sg.generate_sin()

# Load affine matrix
trans_obj = AffineTransform()
trans_obj.loadmatrix('../../../UI_demo/affinematrix_laser0.txt')

#%%
# compute affine matrix
xv, yv = np.meshgrid(
    np.linspace(1, 10, 10),
    np.linspace(1, 10, 10),
)
coord = (list(xv.flatten()), list(yv.flatten()))
pts1= [
    [xv[0, 0], yv[0, 0]], 
    [xv[-1, -1], yv[-1, -1]], 
    [xv[0, -1], yv[0, -1]],
]
# pts2= [
#     [np.random.randint(100), np.random.randint(100)], 
#     [np.random.randint(100), np.random.randint(100)], 
#     [np.random.randint(100), np.random.randint(100)]
# ]
pts2= [
    [xv[0, 0] + 1, yv[0, 0] + 1], 
    [xv[-1, -1] + 1, yv[-1, -1] + 1], 
    [xv[0, -1] + 1, yv[0, -1] + 1],
]
trans_obj = AffineTransform()
trans_obj.getAffineMatrix(pts1, pts2)

#%%
data_trans = trans_obj.affineTrans(coord)

# plt.figure()
# plt.scatter(coord[0], coord[1], s=12)
# plt.scatter(data_trans[0], data_trans[1], s = 12)
# plt.legend(['original', 'transformed'])

plt.figure()
plt.plot(coord[0], coord[1])
plt.plot(data_trans[0], data_trans[1])
plt.legend(['raw', 'trans'])
plt.show()



