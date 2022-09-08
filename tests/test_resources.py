'''
Tests for resources.py
'''

import os

from flywheel_utilities import resources

def test_determine_n_cpus():
    ''' Test determine_n_cpus '''

    # Request sufficiently low number
    req_cpus = 1
    req_omp = 1

    n_cpus, omp_threads = resources.determine_n_cpus(req_cpus, req_omp)

    assert req_cpus == n_cpus
    assert req_omp == omp_threads

    # Request far too many
    req_cpus = 1000
    req_omp = 1000

    n_cpus, omp_threads = resources.determine_n_cpus(req_cpus, req_omp)

    avail_cpus = os.cpu_count()

    assert avail_cpus == n_cpus
    assert avail_cpus == omp_threads


def test_determine_max_mem():
    ''' Test determine_max_mem '''

    # Request sufficiently low amount of mem
    req_mem = 0.5
    assert resources.determine_max_mem(req_mem) == req_mem

    # Request far too much
    req_mem = 1000000000
    assert resources.determine_max_mem(req_mem) < req_mem
