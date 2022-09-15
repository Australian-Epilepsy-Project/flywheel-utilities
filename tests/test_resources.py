'''
Tests for resources.py
'''

import os
import logging

from flywheel_utilities import resources


def test_request_very_few_cpus(caplog):
    ''' Test determine_n_cpus '''

    # Request sufficiently low number
    req_cpus = 1
    req_omp = 1

    with caplog.at_level(logging.INFO):
        n_cpus, omp_threads = resources.determine_n_cpus(req_cpus, req_omp)

    assert req_cpus == n_cpus
    assert req_omp == omp_threads

    assert caplog.messages[1] == "Using 1 cpus (from config)"
    assert caplog.messages[2] == "Using 1 omp_threads (from config)"


def test_request_too_many_cpus(caplog):
    ''' Test requesting too many cpus '''
    # Request far too many
    req_cpus = 1000
    req_omp = 1000

    with caplog.at_level(logging.INFO):
        n_cpus, omp_threads = resources.determine_n_cpus(req_cpus, req_omp)

    avail_cpus = os.cpu_count()

    assert avail_cpus == n_cpus
    assert avail_cpus == omp_threads

    assert caplog.messages[1] == "Requested more cpus than available"
    assert caplog.messages[3] == "Requested more omp_threads than available"


def test_request_very_little_mem(caplog):
    ''' Test determine_max_mem when requesting small amounts '''

    # Request sufficiently low amount of mem
    req_mem = 0.5
    with caplog.at_level(logging.INFO):
        mem = resources.determine_max_mem(req_mem)

    assert mem == req_mem
    assert caplog.messages[2] == "Using 0.5 GiB (from config)"


def test_request_too_much_mem(caplog):
    ''' Test determine_max_mem when requesting too much '''

    # Request far too much
    req_mem = 1000000000
    with caplog.at_level(logging.INFO):
        mem = resources.determine_max_mem(req_mem)

    assert mem < req_mem
    assert caplog.messages[0][:15] == "Systems memory:"
    assert caplog.messages[2] == "Requested more memory than available"
    assert caplog.messages[3][:23] == "Setting memory usage to"
