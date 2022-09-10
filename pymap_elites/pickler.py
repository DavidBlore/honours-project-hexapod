"""Creates checkpoints in order to be able to stop and continue runs of the MAP-Elites algorithm 
"""
import pickle
import gzip
import random
from unittest.mock import DEFAULT

class Pickler:
    """Creates checkpoints in order to be able to stop and continue runs of the MAP-Elites algorithm 

    Args:
        filename_prefix: suffex for the checkpoint file
    """
    DEFAULT_FILENAME_PREFIX = "mapelites-checkpoint-"

    def __init__(self, filename_prefix=DEFAULT_FILENAME_PREFIX):
        self.filename_prefix = filename_prefix
        if filename_prefix is None:
            self.filename_prefix = self.DEFAULT_FILENAME_PREFIX

    def save_checkpoint(self, archive, n_evals, to_evaluate, dim_map, n_niches):
        """Saves current state of MAP-Elites runs to file.

        Args:
            archive: the archive that stores all maps
            n_evals: max number of evaluations
            to_evaluate: parameters that need to be tested 
            dim_map: dimension of the map
            n_niches: number of niches in the map (20k / 40k)
        """
        data = (archive, n_evals, to_evaluate, dim_map, n_niches, random.getstate())

        filename = '{0}{1}.bu'.format(self.filename_prefix.replace(".bu",""), n_evals)
        with gzip.open(filename, 'w', compresslevel=5) as f:
            pickle.dump(data, f)

    @staticmethod
    def restore_checkpoint(filename):
        """Restores previous state of MAP-Elites run from file.

        Args:
            filename: name of checkpoint file

        Returns:
            archive: the archive that stores all maps
            n_evals: max number of evaluations
            to_evaluate: parameters that need to be tested 
            dim_map: dimension of the map
            n_niches: number of niches in the map (20k / 40k)
        """
        with gzip.open(filename) as f:
            archive, n_evals, to_evaluate, dim_map, n_niches, rndstate = pickle.load(f)
            random.setstate(rndstate)
            return (archive, n_evals, to_evaluate, dim_map, n_niches)

