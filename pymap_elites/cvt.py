#! /usr/bin/env python
#| This file is a part of the pymap_elites framework.
#| Copyright 2019, INRIA
#| Main contributor(s):
#| Jean-Baptiste Mouret, jean-baptiste.mouret@inria.fr
#| Eloise Dalin , eloise.dalin@inria.fr
#| Pierre Desreumaux , pierre.desreumaux@inria.fr
#|
#|
#| **Main paper**: Mouret JB, Clune J. Illuminating search spaces by
#| mapping elites. arXiv preprint arXiv:1504.04909. 2015 Apr 20.
#|
#| This software is governed by the CeCILL license under French law
#| and abiding by the rules of distribution of free software.  You
#| can use, modify and/ or redistribute the software under the terms
#| of the CeCILL license as circulated by CEA, CNRS and INRIA at the
#| following URL "http://www.cecill.info".
#|
#| As a counterpart to the access to the source code and rights to
#| copy, modify and redistribute granted by the license, users are
#| provided only with a limited warranty and the software's author,
#| the holder of the economic rights, and the successive licensors
#| have only limited liability.
#|
#| In this respect, the user's attention is drawn to the risks
#| associated with loading, using, modifying and/or developing or
#| reproducing the software by the user in light of its specific
#| status of free software, that may mean that it is complicated to
#| manipulate, and that also therefore means that it is reserved for
#| developers and experienced professionals having in-depth computer
#| knowledge. Users are therefore encouraged to load and test the
#| software's suitability as regards their requirements in conditions
#| enabling the security of their systems and/or data to be ensured
#| and, more generally, to use and operate it in the same conditions
#| as regards security.
#|
#| The fact that you are presently reading this means that you have
#| had knowledge of the CeCILL license and that you accept its terms.

import math
import numpy as np
# from scipy.spatial import cKDTree : TODO -- faster?
from sklearn.neighbors import KDTree
from pymap_elites import common as cm
from pymap_elites.pickler import Pickler

USE_MPI=False
if USE_MPI==True:
    from mpi4py.futures import MPIPoolExecutor
else:
    import multiprocessing

def __add_to_archive(s, centroid, archive, kdt):
    niche_index = kdt.query([centroid], k=1)[1][0][0]
    niche = kdt.data[niche_index]
    n = cm.make_hashable(niche)
    s.centroid = n
    if n in archive:
        if s.fitness > archive[n].fitness:
            archive[n] = s
            return 1
        return 0
    else:
        archive[n] = s
        return 1


# evaluate a single vector (x) with a function f and return a species
# t = vector, function
def __evaluate(t):
    z, f = t  # evaluate z with function f
    fit, desc = f(z)
    return cm.Species(z, desc, fit)

# map-elites algorithm (CVT variant)
def compute(
    dim_map, 
    dim_x, 
    f,
    n_niches=1000,
    max_evals=1e5,
    params=cm.default_params,
    log_file=None,
    variation_operator=cm.variation,
    seeded_individuals=None,
    checkpoint_filenameprefix=None,
    ):
    """CVT MAP-Elites algorithm
    
    Vassiliades V, Chatzilygeroudis K, Mouret JB. Using centroidal voronoi tessellations to scale up the multidimensional archive of phenotypic elites algorithm. IEEE Transactions on Evolutionary Computation. 2017 Aug 3;22(4):623-30.
    Format of the logfile: evals archive_size max mean median 5%_percentile, 95%_percentile

    Args:
        checkpoint_file: File to restore from
        f: Fitness evaluation function. Must return fitness value + descriptor
        continue_checkpointing: continue to checkpoint from this checkpoint
        max_evals: max number of evaluations to run
        params: CVT MAP-Elites paramters
        log_file: file to log to
        variation_operator: evolutionary variation opperator to use 
        seeded_individuals: the individuals to seed the map with (optional) - used for CPG controller
    
    Returns:
        The map (archive)
    """
    # setup the parallel processing pool
    if USE_MPI:
        pool = MPIPoolExecutor()
    else:
        num_cores = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(num_cores)

    # create the CVT
    c = cm.cvt(n_niches, dim_map, params['cvt_samples'], params['cvt_use_cache'])
    kdt = KDTree(c, leaf_size=30, metric='euclidean')
    cm.__write_centroids(c)

    archive = {} # init archive (empty)
    n_evals = 0 # number of evaluations since the beginning
    b_evals = 0 # number evaluation since the last dump
    have_seeded_individuals = False

    # Checkpointer
    pickler = Pickler(checkpoint_filenameprefix) 

    # main loop
    while (n_evals < max_evals):
        to_evaluate = []
        # random initialization
        skip_variation_loop=False
        if seeded_individuals is None:
            if len(archive) <= params['random_init'] * n_niches:
                for i in range(0, params['random_init_batch']):
                    x = np.random.uniform(low=params['min'], high=params['max'], size=dim_x)
                    to_evaluate += [(x, f)]
                skip_variation_loop=True
        elif (seeded_individuals is not None and not have_seeded_individuals):
            for i in range(0, len(seeded_individuals)):
                x = seeded_individuals[i]
                to_evaluate += [(x, f)]
            have_seeded_individuals = True
        else:  # variation/selection loop
            if skip_variation_loop:
                skip_variation_loop=False
            else: 
                keys = list(archive.keys())
                # we select all the parents at the same time because randint is slow
                rand1 = np.random.randint(len(keys), size=params['batch_size'])
                rand2 = np.random.randint(len(keys), size=params['batch_size'])
                for n in range(0, params['batch_size']):
                    # parent selection
                    x = archive[keys[rand1[n]]]
                    y = archive[keys[rand2[n]]]
                    # copy & add variation
                    z = variation_operator(x.x, y.x, params)
                    to_evaluate += [(z, f)]
        # evaluation of the fitness for to_evaluate
        s_list = cm.parallel_eval(__evaluate, to_evaluate, pool, params)
        # natural selection
        for s in s_list:
            __add_to_archive(s, s.desc, archive, kdt)
        # count evals
        n_evals += len(to_evaluate)
        b_evals += len(to_evaluate)

        # write archive
        if b_evals >= params['dump_period'] and params['dump_period'] != -1:
            print("[{}/{}]".format(n_evals, int(max_evals)), end=" ", flush=True)
            cm.__save_archive(archive, n_evals, checkpoint_filenameprefix)
            # if checkpoint_filename_prefix is not None:
            pickler.save_checkpoint(archive, n_evals, to_evaluate, dim_map, n_niches)
            b_evals = 0
        # write log
        if log_file != None:
            fit_list = np.array([x.fitness for x in archive.values()])
            log_file.write("{} {} {} {} {} {} {}\n".format(n_evals, len(archive.keys()),
                    fit_list.max(), np.mean(fit_list), np.median(fit_list),
                    np.percentile(fit_list, 5), np.percentile(fit_list, 95)))
            log_file.flush()
    # END - main loop
    cm.__save_archive(archive, n_evals,name_of_run=checkpoint_filenameprefix)
    # if checkpoint_filename_prefix is not None:
    pickler.save_checkpoint(archive, n_evals, to_evaluate, dim_map, n_niches)
    
    return archive

def compute_from_checkpoint(
    checkpoint_file,
    f,
    continue_checkpointing=True,
    max_evals=1e5,
    params=cm.default_params,
    log_file=None,
    variation_operator=cm.variation,
    seeded_individuals=True,):
    """CVT MAP-Elites algorithm
    
    Vassiliades V, Chatzilygeroudis K, Mouret JB. Using centroidal voronoi tessellations to scale up the multidimensional archive of phenotypic elites algorithm. IEEE Transactions on Evolutionary Computation. 2017 Aug 3;22(4):623-30.
    Format of the logfile: evals archive_size max mean median 5%_percentile, 95%_percentile

    Args:
        checkpoint_file: File to restore from
        f: Fitness evaluation function. Must return fitness value + descriptor
        continue_checkpointing: continue to checkpoint from this checkpoint
        max_evals: max number of evaluations to run
        params: CVT MAP-Elites paramters
        log_file: file to log to
        variation_operator: evolutionary variation opperator to use 
        seeded_individuals: the individuals to seed the map with (optional) - used for CPG controller

    Returns:
        The map (archive)
    """
    # setup the parallel processing pool
    if USE_MPI:
        pool = MPIPoolExecutor()
    else:
        num_cores = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(num_cores)

    # load the checkpoint
    archive, n_evals, to_evaluate, dim_map, n_niches = Pickler.restore_checkpoint(checkpoint_file)
    to_evaluate_seed = []
    for x,y in to_evaluate:
        to_evaluate_seed += [(x, f)]

    # create the CVT
    c = cm.cvt(n_niches, dim_map, params['cvt_samples'], params['cvt_use_cache'])
    kdt = KDTree(c, leaf_size=30, metric='euclidean')
    cm.__write_centroids(c)

    # archive = archive # init archive (empty)
    # n_evals = n_evals # number of evaluations since the beginning
    b_evals = 0 # number evaluation since the last dump
    have_seeded_individuals = False

    # Checkpointer
    pickler = Pickler(checkpoint_file+"-cont-") 

    # main loop
    while (n_evals < max_evals):
        to_evaluate = []
        if (not have_seeded_individuals):
            to_evaluate = to_evaluate_seed
            have_seeded_individuals = True
        else:  # variation/selection loop
            keys = list(archive.keys())
            # we select all the parents at the same time because randint is slow
            rand1 = np.random.randint(len(keys), size=params['batch_size'])
            rand2 = np.random.randint(len(keys), size=params['batch_size'])
            for n in range(0, params['batch_size']):
                # parent selection
                x = archive[keys[rand1[n]]]
                y = archive[keys[rand2[n]]]
                # copy & add variation
                z = variation_operator(x.x, y.x, params)
                to_evaluate += [(z, f)]
        # evaluation of the fitness for to_evaluate
        s_list = cm.parallel_eval(__evaluate, to_evaluate, pool, params)
        # natural selection
        for s in s_list:
            __add_to_archive(s, s.desc, archive, kdt)
        # count evals
        n_evals += len(to_evaluate)
        b_evals += len(to_evaluate)

        # write archive
        if b_evals >= params['dump_period'] and params['dump_period'] != -1:
            print("[{}/{}]".format(n_evals, int(max_evals)), end=" ", flush=True)
            cm.__save_archive(archive, n_evals)
            if continue_checkpointing:
                pickler.save_checkpoint(archive, n_evals, to_evaluate, dim_map, n_niches)
            b_evals = 0
        # write log
        if log_file != None:
            fit_list = np.array([x.fitness for x in archive.values()])
            log_file.write("{} {} {} {} {} {} {}\n".format(n_evals, len(archive.keys()),
                    fit_list.max(), np.mean(fit_list), np.median(fit_list),
                    np.percentile(fit_list, 5), np.percentile(fit_list, 95)))
            log_file.flush()
    cm.__save_archive(archive, n_evals, name_of_run=checkpoint_file)
    if continue_checkpointing:
        pickler.save_checkpoint(archive, n_evals, to_evaluate, dim_map, n_niches)
    
    return archive
