import pickle
import gzip
import random
from unittest.mock import DEFAULT

class Pickler:
    DEFAULT_FILENAME_PREFIX = "mapelites-checkpoint-"

    def __init__(self, filename_prefix=DEFAULT_FILENAME_PREFIX):
        self.filename_prefix = filename_prefix
        if filename_prefix is None:
            self.filename_prefix = self.DEFAULT_FILENAME_PREFIX

    def save_checkpoint(self, archive, n_evals, to_evaluate, dim_map, n_niches):
        data = (archive, n_evals, to_evaluate, dim_map, n_niches, random.getstate())

        filename = '{0}{1}.bu'.format(self.filename_prefix.replace(".bu",""), n_evals)
        with gzip.open(filename, 'w', compresslevel=5) as f:
            pickle.dump(data, f)

    @staticmethod
    def restore_checkpoint(filename):
        with gzip.open(filename) as f:
            archive, n_evals, to_evaluate, dim_map, n_niches, rndstate = pickle.load(f)
            random.setstate(rndstate)
            return (archive, n_evals, to_evaluate, dim_map, n_niches)

