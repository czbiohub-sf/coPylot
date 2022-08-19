from skimage import data

from copylot.gui.viewer.viewer import Viewer


def main():
    camera = data.camera()

    viewer = Viewer(img_data=camera)


if __name__ == '__main__':
    main()
