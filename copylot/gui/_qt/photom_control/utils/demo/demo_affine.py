#%%
import os
import sys
import numpy as np
import cv2
import matplotlib.pyplot as plt
sys.path.append(os.path.join(os.pardir, os.pardir, os.pardir))
from copylot.gui._qt.photom_control.utils.affinetransform import AffineTransform

xv, yv = np.meshgrid(
    np.linspace(1, 10, 10),
    np.linspace(1, 10, 10),
)
dest1 = [2, 2]
dest2 = [11, 11]

xv1 = list(xv.flatten())
yv1 = list(yv.flatten())


pts1= [
    [xv[0, 0], yv[0, 0]], 
    [xv[-1, -1], yv[-1, -1]], 
    [xv[0, -1], yv[0, -1]],
]

#%%
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
trans = AffineTransform()
M = trans.getAffineMatrix(pts1, pts2)
dst = trans.affineTrans([xv1, yv1])

plt.figure()
plt.scatter(xv1, yv1, s=12)
plt.scatter(dst[0], dst[1], s = 12)
plt.legend(['original', 'transformed'])
plt.show()
# %%

ref_cord= [[133.33333333333331, 133.33333333333331], [666.6666666666667, 133.33333333333331], [666.6666666666667, 666.6666666666667], [133.33333333333331, 666.6666666666667]] 
ctrl_cord = [[380.0, 380.0], [420.0, 380.0], [420.0, 420.0], [380.0, 420.0]]
data_list = [[380.0, 420.0, 420.0, 380.0], [380.0, 380.0, 420.0, 420.0]]
#get the coords
x_coords = [point[0] for point in ctrl_cord]
y_coords = [point[1] for point in ctrl_cord]

#get the coords
x_coord_ref = [point[0] for point in ref_cord]
y_coords_ref = [point[1] for point in ref_cord]

trans = AffineTransform()
M = trans.getAffineMatrix(ref_cord, ctrl_cord)
dst = trans.affineTrans(data_list)
print(dst)
# Plot the points as a scatter plot
plt.figure()
plt.scatter(x_coords, y_coords, s=12)
plt.scatter(x_coord_ref, y_coords_ref, s=12)
plt.scatter(dst[0], dst[1], s=12)
plt.legend(['original', 'reference', 'transformed'])
plt.show()
# %%
