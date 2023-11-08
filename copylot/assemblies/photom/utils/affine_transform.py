from collections.abc import Iterable
from warnings import warn

from skimage import transform
import numpy as np
from copylot.assemblies.photom.utils.io import yaml_to_model, model_to_yaml
from copylot.assemblies.photom.utils.settings import AffineTransformationSettings
from pathlib import Path


class AffineTransform:
    """
    A class object for handling affine transformation.
    """

    def __init__(self, config_file='affine_transform.yml'):
        self.config_file = config_file
        settings = yaml_to_model(self.config_file, AffineTransformationSettings)
        self.T_affine = np.array(settings.affine_transform_yx)

    def reset_T_affine(self):
        """
        Reset affine matrix to identity matrix.
        """
        self.T_affine = np.eye(3)

    def get_affine_matrix(self, origin, dest):
        """
        Compute affine matrix from 2 origin & 2 destination coordinates.
        :param origin: 3 sets of coordinate of origin e.g. [(x1, y1), (x2, y2), (x3, y3)]
        :param dest: 3 sets of coordinate of destination e.g. [(x1, y1), (x2, y2), (x3, y3)]
        :return: affine matrix
        """
        if not (isinstance(origin, Iterable) and len(origin) >= 3):
            raise ValueError('origin needs 3 coordinates.')
        if not (isinstance(dest, Iterable) and len(dest) >= 3):
            raise ValueError('dest needs 3 coordinates.')
        self.T_affine = transform.estimate_transform(
            'affine', np.float32(origin), np.float32(dest)
        )
        return self.T_affine

    def apply_affine(self, cord_list):
        """
        Perform affine transformation.
        :param cord_list: a list of origin coordinate (e.g. [[x,y], ...] or [[list for ch0], [list for ch1]])
        :return: destination coordinate
        """
        cord_array = np.stack(cord_list, axis=0)
        if len(cord_list) <= 2:
            cord_array = cord_array.reshape(2, -1)
        else:
            cord_array = cord_array.T
        if self.T_affine is None:
            warn(
                'Affine matrix has not been determined yet. \ncord_list is returned without transformation.'
            )
            dest_list = cord_array
        else:
            cord_array = np.vstack((cord_array, np.ones((1, cord_array.shape[1]))))
            dest_list = self.T_affine @ cord_array
        return [list(i) for i in dest_list]

    # will be used for non numpy & opencv version
    def trans_pointwise(self, cord_list):
        """
        Convert coordinate list from channel wise to point wise.
        (e.g. [[1, 2, 4, .... <ch0>], [4, 2, 5, ... <ch1>] to [[1, 4], [2, 2], ...])
        :param cord_list: coordinate list in channel wise
        :return: coordinate list in point wise
        """
        return list(map(lambda x, y: [x, y], cord_list[0], cord_list[1]))

    # will be used for non numpy & opencv version
    def trans_chwise(self, cord_list):
        """
        Convert coordinate list from channel wise to point wise.
        (e.g. [[1, 4], [2, 2], ...] to [[1, 2, 4, .... <ch0>], [4, 2, 5, ... <ch1>])
        :param cord_list: coordinate list in point wise
        :return: coordinate list in channel wise
        """
        chwise1 = list(map(lambda x: x[0], cord_list))
        chwise2 = list(map(lambda x: x[1], cord_list))
        return [chwise1, chwise2]

    def save_matrix(self, matrix: np.array = None, config_file: Path = None) -> None:
        """
        Save affine matrix to a YAML file.

        Parameters
        ----------
        matrix :np.array, optional
            3x3 affine_transformation, by default None will save the current matrix
        config_file : str, optional
            path to the YAML file, by default None will save to the current config_file.
            This updates the config_file attribute.
        Raises
        ------
        ValueError
            matrix is not defined
        """

        if matrix is None:
            if self.T_affine is None:
                raise ValueError('provided matrix is not defined')
            else:
                matrix = self.T_affine
        else:
            assert matrix.shape == (3, 3)

        if config_file is not None:
            self.config_file = config_file

        model = AffineTransformationSettings(
            affine_transform_yx=np.array(matrix).tolist(),
        )
        model_to_yaml(model, self.config_file)