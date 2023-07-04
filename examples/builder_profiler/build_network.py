import os
import sys
import h5py
import numpy as np
import logging
import cProfile, pstats
import matplotlib.pyplot as plt
from memory_profiler import memory_usage, LogFile, profile, LineProfiler, show_results
import psutil
from functools import partial

from bmtk.builder import NetworkBuilder

try:
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    mpi_rank = comm.Get_rank()
    mpi_size = comm.Get_size()
    barrier = comm.barrier

except ImportError:
    mpi_rank = 0
    mpi_size = 1


# sys.stdout = LogFile('memory_profile_log')
logger = logging.getLogger()


def connect_all2one(sources, target):
    # return np.random.randint(0, 30, size=len(sources))
    src_ids = np.array([s.node_id for s in sources])
    trg_id = target.node_id
    return np.mod(src_ids*trg_id, 13)


def connect_one2one(source, target):
    return np.random.randint(0, 30)


connect_props = {
    'one_to_one': {
        'connection_rule': connect_one2one,
        'iterator': 'one_to_one'    
    },
    'all_to_one': {
        'connection_rule': connect_all2one,
        'iterator': 'all_to_one'    
    }
}



# @profile(stream=fp)
@profile
def build_network(n_nodes=6000, iterator='one_to_one'):
    np.random.seed(100)
    net = NetworkBuilder('net')
    net.add_nodes(N=n_nodes)
    cm = net.add_edges(**connect_props[iterator])
    # cm.add_properties('weight', rule=1.0, dtypes=float)
    net.build()
    net.save(output_dir='network')


def check_edges():
    with h5py.File('network/net_net_edges.h5', 'r') as h5:
        src_ids = h5['/edges/net_to_net/source_node_id'][()]
        trg_ids = h5['/edges/net_to_net/target_node_id'][()]
        nsyns = h5['/edges/net_to_net/0/nsyns'][()]
        check_vals = np.mod(src_ids*trg_ids, 13)
        assert(np.all(check_vals == nsyns))


def setup_logger(n_nodes, iterator, version, profiler):
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    rank_str = '' if mpi_size < 2 else '.rank{}'.format(mpi_rank)
    log_file = f'{profiler}_log.{n_nodes}nodes.{iterator}.{version}{rank_str}.txt'
    if os.path.exists(log_file):
        os.remove(log_file)

    file_logger = logging.FileHandler(log_file)
    file_logger.setFormatter(formatter)
    file_logger.setLevel(logging.DEBUG)
    logger.addHandler(file_logger)

    
def profile_mem(n_nodes, iterator, version):
    setup_logger(n_nodes, iterator, version, 'mem')
    logger.info('---PROFILING MEMORY---')
    
    # show_results_bound = partial(show_results)

    # profiler = LineProfiler()
    # prof_fnc = profiler(build_network)
    # prof_fnc(n_nodes, iterator)
    # show_results(profiler)

    fp = open('memory_profiler.log','w+')

    def add_profiler(*args, **kwargs):
        profiler = LineProfiler(include_children=True)
        prof_fnc = profiler(build_network)
        val = prof_fnc(*args, **kwargs)
        show_results(profiler, stream=fp)
        return val

    # mem = memory_usage((build_network, (n_nodes, iterator)))
    mem = memory_usage((add_profiler, (n_nodes, iterator)))
    print(np.max(mem))

    logger.setLevel(logging.INFO)
    rank_str = '' if mpi_size < 2 else '.rank{}'.format(mpi_rank)
    mem_profile_path = f'mem_plot.{n_nodes}nodes.{iterator}.{version}{rank_str}.png'
    plt.plot(mem)
    plt.savefig(mem_profile_path)


def profile_stats(n_nodes, iterator, version):
    setup_logger(n_nodes, iterator, version, 'run')
    logger.info('---PROFILING RUNTIME---')
    
    pr = cProfile.Profile()
    pr.enable()

    build_network(n_nodes=n_nodes, iterator=iterator)

    pr.disable()
    ps = pstats.Stats(pr)
    ps.dump_stats(f'runtime_profile.{n_nodes}nodes.{iterator}.{version}.stats')


def profile_psutil(n_nodes, iterator, version):
    build_network(n_nodes=n_nodes, iterator=iterator)
    process = psutil.Process()
    print(process.memory_info().rss/(1024.0**2)) 


if __name__ == '__main__':
    version = 'fix_iterator'
    n_nodes = 1000
    # iterator = 'one_to_one'
    iterator = 'all_to_one'
    
    profile_mem(n_nodes=n_nodes, iterator=iterator, version=version)
    # profile_stats(n_nodes=n_nodes, iterator=iterator, version=version)
    # profile_psutil(n_nodes=n_nodes, iterator=iterator, version=version)
    # check_edges()