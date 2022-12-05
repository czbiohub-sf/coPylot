from copylot.hardware.orca_camera.camera import OrcaCamera

if __name__ == '__main__':
    # first define a camera configuration dictionary
    camera_configs={}
    camera_configs['exposure time (ms)'] = 100
    camera_configs['frame number'] = 100
    camera_configs['trigger source'] = 'MASTER PULSE'
    camera_configs['trigger mode'] = 'NORMAL'
    camera_configs['trigger polarity'] = 'POSITIVE'
    camera_configs['trigger times'] = 1
    camera_configs['output trigger kind'] = 'TRIGGER READY'
    camera_configs['output trigger polarity'] = 'POSITIVE'
    camera_configs['master pulse mode'] = 'START'
    camera_configs['burst times'] = 1
    camera_configs['master pulse interval'] = 0.01
    camera_configs['master pulse trigger'] = 'EXTERNAL'
    camera_configs['buffer size (frame number)'] = 200

    # now prepare the camera
    camera = OrcaCamera()

    camera.get_ready(camera_ids=[0])

    camera.set_configurations(camera_configs=camera_configs, camera_ids=[0])

    camera.start(camera_ids=[0])

    p = ''
    while p != 'q':
        p = input('press q to exit ...')

    camera.stop(camera_ids=[0])

    camera.release_buffer(camera_ids=[0])

    camera.close(camera_ids=[0])

