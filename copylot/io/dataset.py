import tensorstore as ts


class Dataset:
    def __init__(
            self,
            path,
            nb_slices: int = 16,
            nb_view: int = 1,
            nb_frames: int = 1,
            y_len: int = 2048,
            x_len: int = 2048,
    ):
        self.ds = ts.open(
            {
                "driver": "zarr",
                'kvstore': {
                    'driver': 'file',
                    'path': path,
                },
                "key_encoding": ".",
                "metadata": {
                    "shape": [nb_slices, nb_view, nb_frames, y_len, x_len],
                    "chunks": [128, 1, 128, 128, 128],
                    "dtype": "<i2",
                    "order": "C",
                    "compressor": {
                        "id": "blosc",
                        "shuffle": -1,
                        "clevel": 5,
                        "cname": "lz4",
                    },
                },
                'create': True,
                'delete_existing': True,
            }
        ).result()

    @property
    def shape(self):
        return self.ds.shape

    # TODO: dtype, channel, etc..

    def sync_write(self):
        raise NotImplementedError

    def async_write(self):
        raise NotImplementedError
