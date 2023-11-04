#%%
import sys
import os
sys.path.append(os.path.join(os.pardir, os.pardir, os.pardir))
import matplotlib.pyplot as plt

from copylot.gui._qt.photom_control.scan_algrthm.scan_algorithm import ScanAlgorithm

#%%
initial_coord = (0, 0)
size = (30, 60)
gap = size[1]
shape = 'square'  # 'disk'  # 
# shape = 'disk'
sec_per_cycle = 1
sg = ScanAlgorithm(initial_coord, size, gap, shape, sec_per_cycle)

# coord = sg.generate_cornerline()
# coord = sg.generate_lissajous()
# coord = sg.generate_sin()
# coord = sg.generate_spiral()
coord = sg.generate_rect()

plt.figure(figsize=(5, 5))
plt.plot(coord[0], coord[1])






# %%
