"""
Determine and set computing resources.
"""

import logging
import os
from math import floor
from typing import Optional, Tuple, Union

import psutil

log = logging.getLogger(__name__)


def determine_n_cpus(n_cpus: int, omp_threads: int) -> Tuple[int, int]:
    """
    Provide the desired number of cpus and threads, and have maximum number allowed returned.

    Parameters
    ----------
    n_cpus:
        number of threads across all processes
    omp_threads:
        number of threads per process

    Returns
    -------
    n_cpus:
        allocated number of threads across all processes
    omp_threads:
        allocated number of threads per process
    """

    avail_cpus: Optional[int] = os.cpu_count()
    assert avail_cpus is not None, "Could not determine available CPUs"

    log.info(f"Available CPUs: {avail_cpus}")

    if n_cpus:
        if n_cpus > avail_cpus:
            log.warning("Requested more cpus than available")
            log.warning(f"Setting to max: {avail_cpus}")
            n_cpus = avail_cpus
        else:
            log.info(f"Using {n_cpus} cpus (from config)")
    else:  # Use maximum available
        n_cpus = avail_cpus
        log.info(f"Using maximum number of cpus: {avail_cpus}")

    # Repeat logic for omp_threads
    if omp_threads:
        if omp_threads > avail_cpus:
            log.warning("Requested more omp_threads than available")
            log.warning(f"Setting to max: {avail_cpus}")
            omp_threads = avail_cpus
        else:
            log.info(f"Using {omp_threads} omp_threads (from config)")
    else:  # Use maximum available
        omp_threads = avail_cpus
        log.info(f"Using maximum number of omp_threads: {avail_cpus}")

    return n_cpus, omp_threads


def determine_max_mem(mem_mb: Union[int, float]) -> float:
    """
    Provide the desired amount of memory and have the maximum allowed memory usage returned.

    Parameters
    ----------
    mem_mb:
        requested memory allocation in GiB

    Returns
    -------
    mem_mb:
        allocated memory (in GiB)
    """

    mem_total = psutil.virtual_memory().total / (1024**3)
    mem_avail = psutil.virtual_memory().available / (1024**3)

    log.info(f"Systems memory: {int(mem_total)} GiB")
    log.info(f"Available memory: {int(mem_avail)} GiB")

    if mem_mb:
        if mem_mb > mem_avail:
            log.warning("Requested more memory than available")
            log.warning(f"Setting memory usage to {floor(mem_avail) - 1}")
            mem_mb = floor(mem_avail) - 1
        else:
            log.info(f"Using {mem_mb} GiB (from config)")
    else:  # Use maximum available
        log.info(f"Setting memory usage to {floor(mem_avail)-1} GiB")
        mem_mb = floor(mem_avail) - 1

    return mem_mb
