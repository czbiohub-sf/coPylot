#%%
from copylot.hardware.lasers.vortran import vortran

def demo_get_laser_list():
    laser_list = vortran.VoltranLaser.get_lasers()
    print(laser_list)

def demo_toggle_emission():
    laser_list = vortran.VoltranLaser.get_lasers()
    laser = vortran.VoltranLaser(port=laser_list[0][0])
    laser.toggle_emission = 1 
    laser.toggle_emission = 0
    laser.disconnect()

if __name__ == '__main__':
    demo_get_laser_list()
    demo_toggle_emission()

