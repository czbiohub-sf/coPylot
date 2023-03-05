#%%
from copylot.hardware.lights.voltran import voltran

def demo_get_laser():
    laser_list = voltran.get_lasers()
    print(laser_list)

def demo_voltran():
    laser_list = voltran.get_lasers()
    laser = voltran.VoltranLaser(port=laser_list[0][0])
    laser.disconnect()

def demo_send_cmd():
    laser_list = voltran.get_lasers()
    print(laser_list[0][0])
    with voltran.VoltranLaser(port=laser_list[0][0]) as laser:
        print(laser.laser_power)
        
if __name__ == '__main__':
    demo_get_laser()
    demo_voltran()
    demo_send_cmd()
# %%
