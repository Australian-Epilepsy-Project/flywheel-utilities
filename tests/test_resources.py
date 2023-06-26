"""
Tests for resources.py
"""

import os

from flywheel_utilities import resources


def test_det_n_cpus_sufficient():
    """Test requesting cpus when amply available"""

    # Request sufficiently low number
    req_cpus = 1
    req_omp = 1

    n_cpus, omp_threads = resources.determine_n_cpus(req_cpus, req_omp)

    assert req_cpus == n_cpus
    assert req_omp == omp_threads


def test_det_n_cpus_too_many():
    """Test requestin too many cpus"""

    # Request far too many
    req_cpus = 1000
    req_omp = 1000

    n_cpus, omp_threads = resources.determine_n_cpus(req_cpus, req_omp)

    avail_cpus = os.cpu_count()

    assert avail_cpus == n_cpus
    assert avail_cpus == omp_threads


def test_det_n_cpus_no_args():
    """Test requesting max cpus by not providing arguments"""

    n_cpus, omp_threads = resources.determine_n_cpus()

    avail_cpus = os.cpu_count()

    assert avail_cpus == n_cpus
    assert avail_cpus == omp_threads


def test_det_max_mem_sufficient():
    """Test determine_max_mem"""

    # Request sufficiently low amount of mem
    req_mem = 0.5
    assert resources.determine_max_mem(req_mem) == req_mem


def test_det_max_mem_req_too_much():
    """Test requesting too much memory"""

    # Request far too much
    req_mem = 1000000000
    assert resources.determine_max_mem(req_mem) < req_mem
