import pytest

from partition_count import (gen_next_part, get_part_cnt,
                             gen_edge_partitions_by_term_iteration,
                             get_edge_partitions_by_term_iteration_cnt,
                             SmallLengthPartitionsStopIteration)
from partition_utils import get_term_iteration_interval
from utils import save_to_csv


def test_gen_next_part():
    cnt = 0
    init_part = [1, 2, 3, 94]
    for _ in gen_next_part(init_part, 100, 0, 100):
        cnt += 1
    assert cnt == 5952

    init_part = [1, 2, 3, 4, 10]
    res = [
        [1, 2, 3, 4, 10],
        [1, 2, 3, 5, 9],
        [1, 2, 3, 6, 8],
    ]
    idx = 3
    for i, part in enumerate(gen_next_part(init_part, 20, idx, 20)):
        assert part == res[i]

    init_part = [1, 2, 4, 5, 9]
    res = [
        [1, 2, 4, 5, 9],
        [1, 2, 4, 6, 8],
        [1, 2, 5, 6, 7],
    ]
    idx = 2
    for i, part in enumerate(gen_next_part(init_part, 21, idx, 21)):
        assert part == res[i]

    init_part = [1, 5, 6, 7, 8, 11, 12]
    res = [
        [1, 5, 6, 7, 8, 11, 12],
        [1, 5, 6, 7, 9, 10, 12],
        [1, 5, 6, 8, 9, 10, 11],
    ]
    for i, part in enumerate(gen_next_part(init_part, 50, 1, 50)):
        assert part == res[i]

    cnt = 0
    init_part = [1, 2, 3, 4, 90]
    for _ in gen_next_part(init_part, 100, 0, 100):
        cnt += 1
    assert cnt == 25337


def test_gen_next_part_last_term_limit():
    cnt = 0
    init_part = [1, 2, 3, 4, 15]
    res = [
        [1, 3, 6, 7, 8],
        [1, 4, 5, 7, 8],
        [2, 3, 5, 7, 8],
        [2, 4, 5, 6, 8],
        [3, 4, 5, 6, 7],
    ]
    for i, part in enumerate(gen_next_part(init_part, 25, 0, 9)):
        assert part == res[i]
        cnt += 1
    assert cnt == 5


def test_get_part_cnt():
    init_part = [1, 2, 3, 4, 15]
    cnt = get_part_cnt(init_part, 25, 0, 25)
    assert cnt == 30

    init_part = [1, 3, 4, 5, 12]
    cnt = get_part_cnt(init_part, 25, 1, 25)
    assert cnt == 9

    init_part = [1, 2, 4, 5, 9]
    with pytest.raises(ValueError):
        # idx should be less than n-4
        _ = get_part_cnt(init_part, 21, 2, 21)

    init_part = [1, 2, 3, 4, 90]
    cnt = get_part_cnt(init_part, 100, 0, 100)
    assert cnt == 25337

    init_part = [1, 2, 3, 4, 191]
    cnt = get_part_cnt(init_part, 201, 0, 201)
    assert cnt == 486424

    init_part = [1, 2, 3, 4, 5, 6, 29]
    cnt = get_part_cnt(init_part, 50, 0, 50)
    assert cnt == 522

    init_part = [1, 2, 3, 94]
    cnt = get_part_cnt(init_part, 100, 0, 100)
    assert cnt == 5952


def test_get_part_cnt_last_term_limit():
    init_part = [1, 2, 3, 4, 15]
    cnt = get_part_cnt(init_part, 25, 0, 9)
    assert cnt == 5


def test_gen_edge_partitions_by_term_iteration():
    s = 50
    n = 7
    cnt = 0
    for part in gen_edge_partitions_by_term_iteration(s, n, 0, 2):
        #print(part)
        cnt += 1
    assert cnt == 20


def test_get_edge_partitions_by_term_iteration_cnt():
    cnt, _ = get_edge_partitions_by_term_iteration_cnt(21, 5, 0, 1)
    assert cnt == 3

    cnt, _ = get_edge_partitions_by_term_iteration_cnt(201, 5, 0, 1)
    assert cnt == 9987


def test_get_edge_partitions_by_term_iteration_cnt_diff():
    cnt_p_49_7 = 436
    cnt_p_50_7 = 522
    _diff = cnt_p_50_7 - cnt_p_49_7
    cnt = 0
    s = 50
    n = 7
    _min, _max = get_term_iteration_interval(s, n, 0)
    for j in range(_min, _max):
        _cnt, is_stop = get_edge_partitions_by_term_iteration_cnt(s, n, 0, j)
        cnt += _cnt
        if is_stop:
            break
    assert cnt == _diff  # 86


def test_get_edge_partitions_by_term_iteration_cnt_play():
    cnt, _ = get_edge_partitions_by_term_iteration_cnt(500, 20, 0, 1)
    assert cnt == 9987

