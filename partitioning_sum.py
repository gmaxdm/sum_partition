""" Partitioning sum
    Conditions:
    given an array of distinct integers in ascending order

    Constraints:
    1 <= candidates.length <= 100
    1 <= candidates[i] <= 256
    All elements of candidates are distinct.
"""
import multiprocessing
import time
import logging

from typing import List
from multiprocessing import Pool

from mongo.client import init_mongo, get_client
from partition_count import (get_part_cnt, gen_next_part,
                             gen_edge_partitions_by_term_iteration,
                             get_edge_partitions_by_term_iteration_cnt,
                             SmallLengthPartitionsStopIteration)
from partition_utils import (ap_sum, get_ap_left_part_sum, get_term_iteration_interval,
                             get_init_partition, get_partitions_cnt_by_term_iteration)
from compression_utils import (gen_ordered_numbers, compress_layer, gen_bytes, split_by_layers,
                               print_layers_stat, NUM_LEN)
from utils import save_to_csv
from logger.logger import setup_logging


setup_logging(path='logger/logger.yaml')
logger = logging.getLogger('partition')


class Solution:
    def partitioningSum(self, candidates: List[int], target: int) -> List[List[int]]:
        pass


def sum_partitioning(s: int, n: int) -> List[List[int]]:
    """
    Returns partitionings with distinct n terms in ascended order only.
    Part(20,5)
    idx=3
    1	2	3	4	10
    1	2	3	5	9
    1	2	3	6	8

    idx=2
    1	2	4	5	8
    1	2	4	6	7

    idx=1
    1	3	4	5	7

    idx=0
    2	3	4	5	6

    :param s: sum
    :param n: number of terms
    :return: list of all partitionings
    """
    if n < 3:
        raise Exception("terms number should be at least 3")

    _first_part_div = [*range(1, n)]
    _first_part_div_sum = get_ap_left_part_sum(0, 1, n)
    if _first_part_div_sum > s:
        raise Exception("sum partitioning failed: number of terms exceeds sum")
    if s - _first_part_div_sum < _first_part_div[-1]:
        raise Exception("sum partitioning failed: last term is smaller than previous one. All terms must be in ascending order.")

    init_part = [*_first_part_div, s - _first_part_div_sum]
    start_time = time.perf_counter()
    partitionings = _run_serial(s, n)
    end_time = time.perf_counter()
    logger.info(f"[SERIAL] Execution time: {end_time - start_time:.6f} seconds")
    _l1 = len(partitionings)

    start_time = time.perf_counter()
    partitionings = _run_in_pool(s, n)
    end_time = time.perf_counter()
    logger.info(f"[POOL] Execution time: {end_time - start_time:.6f} seconds")
    _l2 = len(partitionings)
    assert _l1 == _l2
    return partitionings


def sum_partition_idx(s: int, n: int, term_idx: int, iteration: int) -> List[List[int]]:
    parts = []
    try:
        _init_part = get_init_partition(s, n, term_idx, iteration)
    except ValueError:
        return parts

    for part in gen_next_part(_init_part, s, term_idx, s):
        parts.append(part)
    return parts

def _run_in_pool(s:int, n: int) -> List[List[int]]:
    logger.info("cpu count:", multiprocessing.cpu_count())

    _args = []
    for i in range(n - 3):
        _args.append((s, n, i, i+2))
    # for term_idx == n-3 we need to have iteration i+1
    _args.append((s, n, n-3, n-2))

    parts: List[List[int]] = []
    with Pool(processes=multiprocessing.cpu_count()) as pool:
        for res in pool.starmap(sum_partition_idx, _args):
            parts.extend(res)
    return parts

def _run_serial(s:int, n: int) -> List[List[int]]:
    # serial:
    parts = []
    for i in range(n - 3):
        parts.extend(sum_partition_idx(s, n, i, i+2))
    # for term_idx == n-3 we need to have iteration i+1
    parts.extend(sum_partition_idx(s, n, n-3, n-2))
    return parts


def sum_partition_idx_iteration_count(s: int, n: int, term_idx: int, iteration: int) -> int:
    logger.info(f"s: {s}, n: {n}, term_idx: {term_idx}, iteration: {iteration}")
    try:
        _init_part = get_init_partition(s, n, term_idx, iteration)
    except ValueError:
        return 0

    logger.info("init part", _init_part)
    cnt = get_part_cnt(_init_part, s, term_idx)
    return cnt


def sum_partition_cnt(s: int, n: int) -> int:
    """
    calc sum partitions count. Use Pool of workers. Each worker takes the partitions by index.
    Iteration for the index must be i+1, like 2, 3, 4, 5, 10 for index 0.
    For the last n-3 index the iteration should be i.
    :param s:
    :param n:
    :return:
    """
    logger.info("cpu count:", multiprocessing.cpu_count())

    _args = []
    for i in range(n - 3):
        _args.append((s, n, i, i + 2))

    cnt = 0
    with Pool(processes=multiprocessing.cpu_count()) as pool:
        for res in pool.starmap(sum_partition_idx_iteration_count, _args):
            cnt += res
    logger.info(cnt)
    # for term_idx == n-3 we need to have iteration i
    parts = sum_partition_idx(s, n, n - 3, n - 2)
    cnt += len(parts)
    logger.info(cnt)
    return cnt


def get_partitions_index_by_term_iteration(s: int, n: int, term_idx: int, iteration: int, last_term: int) -> int:
    if term_idx >= n - 1:
        raise Exception("term index exceeds n - 1")

    _idx = 0
    for i in range(term_idx):
        _min, _max = get_term_iteration_interval(s, n, i)
        for j in range(_min + 1, _max + 1):
            _idx += get_partitions_cnt_by_term_iteration(s, n, i, j)

    _min, _max = get_term_iteration_interval(s, n, term_idx)
    for j in range(_min + 1, iteration):
        _idx += get_partitions_cnt_by_term_iteration(s, n, term_idx, j)

    # get_min_partition_by_idx_iteration last term:
    left_sum = ap_sum(1, term_idx)
    right_sum = ap_sum(iteration, n - term_idx - 1)
    p1 = s - left_sum - right_sum
    _idx += p1 - last_term + 1
    return _idx


def find_partition_diff_by_idx(s: int, n: int, idx: int) -> List[List[int]]:
    parts = []
    if n < 3:
        return parts
    if idx > n - 2:
        return parts

    _min, _max = get_term_iteration_interval(s, n, idx)
    for j in range(_min + 1, _max + 1):
        try:
            for _part in gen_edge_partitions_by_term_iteration(s, n, idx, j):
                parts.append(_part)
        except SmallLengthPartitionsStopIteration:
            break
    return parts


def _run_diff_serial(s: int, n: int) -> List[List[int]]:
    parts = []
    for idx in range(n-1):
        parts.extend(find_partition_diff_by_idx(s, n, idx))
    return parts


def _run_diff_in_pool(s: int, n: int) -> List[List[int]]:
    parts = []
    with Pool(processes=multiprocessing.cpu_count()) as pool:
        for res in pool.starmap(find_partition_diff_by_idx, [(s, n, i) for i in range(n-1)]):
            parts.extend(res)
    return parts

def get_partition_diff_by_searching(s: int, n: int) -> List[List[int]]:
    """
    Returns partitions of s that are unique for s and don't exist in s-1.
    Use search method.
    :param s:
    :param n:
    :return:
    """
    #_min_sum = ap_sum(1, n)
    #length = min(s-_min_sum, n-1)

    start_time = time.perf_counter()
    parts = _run_diff_serial(s, n)
    end_time = time.perf_counter()
    logger.info(f"[SERIAL] Execution time: {end_time - start_time:.6f} seconds")

    #start_time = time.perf_counter()
    #parts = _run_diff_in_pool(s, n)
    #end_time = time.perf_counter()
    #logger.info(f"[POOL] Execution time: {end_time - start_time:.6f} seconds")
    return parts


def calc_sum_gen_partitions_count_by_diff(sum_from: int, sum_to: int, from_cnt: int, n: int) -> int:
    _min_sum = ap_sum(1, n)
    cnt = from_cnt
    if sum_from < _min_sum:
        sum_from = _min_sum
        cnt = 1
    with Pool(processes=multiprocessing.cpu_count()) as pool:
        for res in pool.starmap(_run_diff_serial, [(_s, n) for _s in range(sum_from+1, sum_to+1)]):
            cnt += len(res)
    logger.info(f"cnt: {cnt}, fits 4 bytes size ({2**32}): {cnt < 2**32}")
    return cnt


def run_compressions():
    nums = gen_ordered_numbers(NUM_LEN)
    zlib_compressed = compress_layer(nums, "ZLIB")
    ratio = len(zlib_compressed) / len(nums)
    logger.info("zlib", ratio)

    lzma_compressed = compress_layer(nums, "LZMA")
    ratio = len(lzma_compressed) / len(nums)
    logger.info("lzma", ratio)


def compression_try(ordered_nums: List[int]):
    logger.info("len", len(ordered_nums))
    zlib_compressed = compress_layer(ordered_nums, "ZLIB")
    ratio = len(zlib_compressed) / len(ordered_nums)
    logger.info("zlib", ratio)

    lzma_compressed = compress_layer(ordered_nums, "LZMA")
    ratio = len(lzma_compressed) / len(ordered_nums)
    logger.info("lzma", ratio)


def partitioning_try():
    _cnt = 0
    init_part = get_init_partition(500, 10, 7, 8)
    logger.info("init:", init_part)
    for part in gen_next_part(init_part, 500, 7, 500):
        _cnt += 1
        #logger.info(part)
    logger.info("Count:", _cnt)


def partitioning_cnt_try():
    init_part = get_init_partition(200, 10, 7, 9)
    logger.info("init:", init_part)
    cnt = get_part_cnt(init_part, 200, 7)
    logger.info("Count:", cnt)


def save_sum_partitions(s: int, n: int, save_csv: bool=False):
    parts = sum_partitioning(s, n)
    #logger.info(parts)
    logger.info("count:", len(parts))
    if save_csv:
        save_to_csv(f"sum_partition/csv/{s}_{n}.csv", parts)

def save_sum_partitions_diff(s: int, n: int, save_csv: bool=False):
    parts = get_partition_diff_by_searching(s, n)
    #logger.info(parts)
    logger.info("count:", len(parts))
    if save_csv:
        save_to_csv(f"sum_partition/csv/{s}_{n}_diff.csv", parts)


def get_partition_diff_by_term_cnt(s: int, n: int) -> int:
    """
    get partitions that are new in S in difference with S-1
    :param s:
    :param n:
    :return:
    """
    cnt = 0
    if n < 3:
        return cnt

    _mongo = get_client()

    cnt = _mongo.get_diff(s, n)
    if cnt:
        logger.info(f"D({s}, {n}) = {cnt} (getting from cache)")
        return cnt

    cnt = 0
    _min, _max = get_term_iteration_interval(s, n, 0)
    logger.info(f"s: {s}, n: {n}, min: {_min}, max: {_max}")
    for j in range(_min, _max + 1):
        _cnt = _mongo.get_edge(s, n, j)
        if _cnt:
            cnt += _cnt
            logger.info(f"E({s}, {n}, 0, {j}) = {_cnt} (getting from cache)")
            continue

        _cnt, is_stop = get_edge_partitions_by_term_iteration_cnt(s, n, 0, j)
        _mongo.add_edge(s, n, j, _cnt)
        logger.info(f"E({s}, {n}, 0, {j}) = {_cnt}")
        cnt += _cnt
        if is_stop:
            break
    _mongo.add_diff(s, n, cnt)
    logger.info(f"D({s}, {n}) = {cnt}")
    return cnt


def calc_sum_partitions_count_by_diff(sum_from: int, sum_to: int, from_cnt: int, n: int) -> int:
    _mongo = get_client()
    cnt = _mongo.get_part(sum_to, n)
    if cnt:
        logger.info(f"P({sum_to}, {n}) = {cnt} (getting from cache)")
        return cnt

    _min_sum = ap_sum(1, n)
    cnt = from_cnt
    if sum_from < _min_sum:
        sum_from = _min_sum
        cnt = 1
    with Pool(processes=multiprocessing.cpu_count(), initializer=init_mongo) as pool:
        for res in pool.starmap(get_partition_diff_by_term_cnt, [(_s, n) for _s in range(sum_from+1, sum_to+1)]):
            cnt += res
    _mongo.add_part(sum_to, n, 1, cnt)
    logger.info(f"P({sum_to}, {n}) = {cnt}")
    logger.info(f"cnt: {cnt}, fits 4 bytes size ({2**32}): {cnt < 2**32}")
    return cnt


def sum_partition_count(s: int, n: int, term_idx: int, iteration: int) -> int:
    _cnt = 0
    init_part = get_init_partition(s, n, term_idx, iteration)
    for _ in gen_next_part(init_part, s, term_idx, s):
        _cnt += 1
    return _cnt


def calc_sum_partition_count_by_formula(s: int, n: int) -> int:
    """
    Calc sum partition count by formula (see partitions.ods in csv dir, sheet nested formula).
    _min_p = P(S-n+2, 3, 0, 3)
    :param s:
    :param n:
    :return:
    """
    _cnt = sum_partition_count(s-n+2, 3, 0, 3)

    with Pool(processes=multiprocessing.cpu_count()) as pool:
        for res in pool.starmap(sum_partition_count, [(s-i, n-i, 0, i+2) for i in range(n-3)]):
            _cnt += res
    logger.info(f"cnt: {_cnt}, fits 4 bytes size ({2**32}): {_cnt < 2**32}")
    return _cnt


def partition_index():
    # [12, 453, 501, 738, 1345, 1589, 2127, 3289, 4967, 5459]
    idx = get_partitions_index_by_term_iteration(20480, 10, 0, 12, 5459)
    logger.info("P(20480, 10, 0, 12, 5459) - ", idx)

    # [2, 3, 4, 18, 74]
    idx = get_partitions_index_by_term_iteration(101, 5, 0, 2, 74)
    logger.info("P(101, 5, 0, 2, 74) - ", idx)

    # [15, 17, 19, 20, 30]
    idx = get_partitions_index_by_term_iteration(101, 5, 0, 15, 30)
    logger.info("P(101, 5, 0, 15, 30) - ", idx)


def main():
    start_time = time.perf_counter()

    #logger.info("get_part_cnt([1, 2, 3, 4, 5, 6, 7, 8, 9, 455], 500, 0)")
    #cnt = get_part_cnt([1, 2, 3, 4, 5, 6, 7, 8, 9, 455], 500, 0)
    #if cnt == 886831799718:
    #    logger.info("test has passed OK")
    #else:
    #    logger.info(f"test failed: 886831799718 (expected) != {cnt} (actual)")

    #run_compressions(layers[0])
    #compression_try()
    #partitioning_try()
    #partitioning_cnt_try()
    #logger.info("sum_partition_cnt(500, 10)")
    #sum_partition_cnt(500, 10)
    #save_sum_partitions(1000, 10, save_csv=False)
    #save_sum_partitions_diff(5001, 10, save_csv=False)

    logger.info("calc_sum_partitions_count_by_diff(300, 500, 6194373023, 10)")
    calc_sum_partitions_count_by_diff(300, 500, 6194373023, 10)
    #calc_sum_partition_count_by_formula(1000, 10)
    #calc_sum_partitions_count(31000, 40960, 497109647, 20)
    #parts = _run_diff_serial(50, 7)
    #logger.info(parts)
    #logger.info(len(parts))
    #partition_index()
    #s = find_partition_diff_by_idx(50, 7, 4)
    #logger.info(s)
    #logger.info(len(s))
    end_time = time.perf_counter()
    logger.info(f"Execution time: {end_time - start_time:.6f} seconds")


if __name__ == "__main__":
    main()

