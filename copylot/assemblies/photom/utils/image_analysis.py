import numpy as np
from skimage.feature import peak_local_max
from skimage import filters
from skimage.filters import gaussian


def find_objects_centroids(image, sigma=5, threshold_rel=0.5, min_distance=10):
    """
    Calculate the centroids of blurred objects in an image.

    Parameters:
    - image: 2D numpy array, single frame from the fluorescence microscopy data.
    - sigma: Standard deviation for Gaussian filter to smooth the image.
    - threshold_rel: Relative threshold for detecting peaks. Adjust according to image contrast.
    - min_distance: The minimum distance between peaks detected.

    Returns:
    - centroids: (N, 2) array where each row is (row, column) of an object's centroid.
    """
    # Smooth the image to enhance peak detection
    smoothed_image = gaussian(image, sigma=sigma)

    # Thresholding to isolate objects
    threshold_value = filters.threshold_otsu(smoothed_image)
    binary_image = smoothed_image > threshold_value * threshold_rel

    # Detect peaks which represent object centroids
    coordinates = peak_local_max(
        smoothed_image,
        min_distance=min_distance,
        threshold_abs=threshold_value * threshold_rel,
    )

    return coordinates


def calculate_centroids(image_sequence, sigma=5, threshold_rel=0.5, min_distance=10):
    """
    Calculate the centroids of objects in a sequence of images.

    Parameters:
    - image_sequence: 3D numpy array, sequence of frames from the fluorescence microscopy data.
    - sigma: Standard deviation for Gaussian filter to smooth the image.
    - threshold_rel: Relative threshold for detecting peaks. Adjust according to image contrast.
    - min_distance: The minimum distance between peaks detected.

    Returns:
    - centroids: (N, 2) array where each row is (row, column) of an object's centroid.
    """
    centroids = []
    for frame in image_sequence:
        frame_centroids = find_objects_centroids(
            frame, sigma=sigma, threshold_rel=threshold_rel, min_distance=min_distance
        )
        centroids.append(frame_centroids)
    return np.array(centroids)
