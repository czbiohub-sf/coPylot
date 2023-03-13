import os
import sys
import numpy as np
import cv2
import matplotlib.pyplot as plt
sys.path.append(os.path.join(os.pardir, os.pardir, os.pardir))
from widgets.utils.affinetransform import AffineTransform

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
