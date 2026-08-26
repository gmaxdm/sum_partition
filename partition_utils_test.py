import pytest

from partition_utils import (get_ap_left_part_sum, get_init_partition, get_term_interval, get_min_part_last_term,
                             get_partitions_cnt_by_term_iteration, get_partition_by_term_iteration_ap_min_last,
                             get_partition_by_term_ap_max_last, get_partition_by_term_iteration_ap_min_first,
                             get_tail_partition_iteration_cnt, get_partition_by_term_iteration_ap_max_last)


def test_get_ap_left_part_sum():
    s = get_ap_left_part_sum(2, 4, 5)
    assert s == 12

    s = get_ap_left_part_sum(0, 2, 5)
    assert s == 14

    s = get_ap_left_part_sum(0, 1, 6)
    assert s == 15


def test_get_init_partition():
    part = get_init_partition(20, 5, 0, 2)
    assert part == [2, 3, 4, 5, 6]

    part = get_init_partition(100, 5, 1, 3)
    assert part == [1, 3, 4, 5, 87]

    part = get_init_partition(20, 5, 3, 5)
    assert part == [1, 2, 3, 5, 9]

    part1 = get_init_partition(101, 5, 0, 1)
    part2 = get_init_partition(101, 5, 3, 4)
    assert part1 == part2


def test_get_term_interval():
    _min, _max = get_term_interval(25, 5, 0)
    assert _min == 1
    assert _max == 3

    _min, _max = get_term_interval(22, 5, 2)
    assert _min == 3
    assert _max == 5

    _min, _max = get_term_interval(21, 5, 3)
    assert _min == 4
    assert _max == 7

    _min, _max = get_term_interval(25, 5, 2)
    assert _min == 3
    assert _max == 6

    _min, _max = get_term_interval(25, 5, 3)
    assert _min == 4
    assert _max == 9

    _min, _max = get_term_interval(101, 5, 2)
    assert _min == 3
    assert _max == 31


def test_get_partition_by_term_iteration_ap_max_last():
    # ap max last
    part = get_partition_by_term_iteration_ap_max_last(50, 7, 0, 1)
    assert part == [1, 5, 6, 7, 8, 11, 12]

    # max last
    # part = get_partition_by_term_iteration_max_last(50, 7, 0, 1)
    # assert part == [1, 5, 6, 8, 9, 10, 11]

    part = get_partition_by_term_iteration_ap_max_last(50, 7, 1, 3)
    assert part == [1, 3, 7, 8, 9, 10, 12]

    part = get_partition_by_term_iteration_ap_max_last(1000, 7, 0, 1)
    assert part == [1, 164, 165, 166, 167, 168, 169]


def test_get_min_partition_by_term_iteration():
    part = get_partition_by_term_iteration_ap_min_last(23, 5, 1, 4)
    assert part == [1, 4, 5, 6, 7]

    part = get_partition_by_term_iteration_ap_min_last(25, 5, 2, 5)
    assert part == [1, 2, 5, 8, 9]

    part = get_partition_by_term_iteration_ap_min_last(23, 5, 3, 5)
    assert part == [1, 2, 3, 5, 12]

    part = get_partition_by_term_iteration_ap_min_last(101, 5, 2, 4)
    assert part == [1, 2, 4, 46, 48]


def test_get_max_partition_by_term():
    part = get_partition_by_term_ap_max_last(101, 5, 0)
    assert part == [18, 19, 20, 21, 23]

    part = get_partition_by_term_ap_max_last(101, 5, 2)
    assert part == [1, 2, 31, 33, 34]

    part = get_partition_by_term_ap_max_last(23, 5, 1)
    assert part == [1, 4, 5, 6, 7]

    part = get_partition_by_term_ap_max_last(50, 7, 0)
    assert part == [4, 5, 6, 7, 8, 9, 11]

    # ap max last
    part = get_partition_by_term_ap_max_last(50, 7, 1)
    assert part == [1, 5, 6, 7, 8, 11, 12]

    # max last
    # part = get_partition_by_term_max_last(50, 7, 1)
    # assert part == [1, 5, 6, 8, 9, 10, 11]

    part = get_partition_by_term_ap_max_last(1000, 7, 1)
    assert part == [1, 164, 165, 166, 167, 168, 169]


def test_get_min_partition_by_idx_iteration():
    part = get_partition_by_term_iteration_ap_min_first(25, 5, 1, 3)
    assert part == [1, 3, 4, 5, 12]
    part = get_partition_by_term_iteration_ap_min_first(25, 5, 2, 4)
    assert part == [1, 2, 4, 5, 13]


def test_get_partitions_cnt_by_term_iteration():
    # 2, 3, 4, 5, 11
    # 2, 3, 4, 6, 10
    # 2, 3, 4, 7, 9
    cnt = get_partitions_cnt_by_term_iteration(25, 5, 0, 2)
    assert cnt == 3

    # 3, 4, 5, 6, 7
    cnt = get_partitions_cnt_by_term_iteration(25, 5, 0, 3)
    assert cnt == 1

    # 1, 2, 3, 5, 12
    cnt = get_partitions_cnt_by_term_iteration(23, 5, 3, 5)
    assert cnt == 1


def test_get_tail_partition_iteration_cnt():
    # [1, 3, 4, 5, 12]
    cnt = get_tail_partition_iteration_cnt(25, 4, 4)
    assert cnt == 4

    # [1, 3, 6, 7, 8]
    cnt = get_tail_partition_iteration_cnt(25, 4, 6)
    assert cnt == 1

    cnt = get_tail_partition_iteration_cnt(10, 4, 4)
    assert cnt == 0

    # [1, 2, 4, 5, 13]
    cnt = get_tail_partition_iteration_cnt(25, 3, 4)
    assert cnt == 4

    # [1, 2, 4, 5, 6, 7]
    cnt = get_tail_partition_iteration_cnt(25, 7, 5)
    assert cnt == 1


def test_get_tail_partition_iteration_cnt_last_term_limit():
    # [1, 3, 4, 5, 12]
    cnt = get_tail_partition_iteration_cnt(25, 4, 4, last_term_limit=11)
    assert cnt == 2

    # [1, 3, 6, 7, 8]
    cnt = get_tail_partition_iteration_cnt(25, 4, 6, last_term_limit=9)
    assert cnt == 1

    cnt = get_tail_partition_iteration_cnt(10, 4, 4, last_term_limit=4)
    assert cnt == 0

    # [1, 2, 4, 5, 13]
    cnt = get_tail_partition_iteration_cnt(25, 3, 4, last_term_limit=11)
    assert cnt == 1

    # [1, 2, 4, 5, 6, 7]
    cnt = get_tail_partition_iteration_cnt(25, 7, 5, last_term_limit=8)
    assert cnt == 1

    # [1, 2, 4, 5, 6, 7]
    cnt = get_tail_partition_iteration_cnt(25, 7, 5, last_term_limit=7)
    assert cnt == 0


def test_get_min_part_last_term():
    _max_ceil = get_min_part_last_term(25, 5, 1)
    assert _max_ceil == 15

    _max_ceil = get_min_part_last_term(25, 5, 3)
    assert _max_ceil == 7

