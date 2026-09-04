import pytest

from partition_count import (gen_next_part, _get_part_cnt, get_part_count_ceil,
                             get_part_count_ceil_by_prev_ceil, get_max_partition,
                             get_term_iteration_max_part,
                             gen_edge_partitions_by_term_iteration,
                             get_edge_partitions_by_term_iteration_cnt)
from partition_utils import (get_term_interval, get_init_partition_ceil)


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
    init_part = [1, 2, 3, 4, 5]
    cnt = _get_part_cnt(init_part, 15, 0)
    assert cnt == 1

    init_part = [1, 2, 3, 4, 15]
    cnt = _get_part_cnt(init_part, 25, 0)
    assert cnt == 30

    init_part = [1, 3, 4, 5, 12]
    cnt = _get_part_cnt(init_part, 25, 1)
    assert cnt == 9

    init_part = [1, 2, 4, 5, 9]
    with pytest.raises(ValueError):
        # idx should be less than n-4
        _ = _get_part_cnt(init_part, 21, 2)

    init_part = [1, 2, 3, 4, 90]
    cnt = _get_part_cnt(init_part, 100, 0)
    assert cnt == 25337

    init_part = [1, 2, 3, 4, 191]
    cnt = _get_part_cnt(init_part, 201, 0)
    assert cnt == 486424

    init_part = [1, 2, 3, 4, 5, 6, 29]
    cnt = _get_part_cnt(init_part, 50, 0)
    assert cnt == 522

    init_part = [1, 2, 3, 94]
    cnt = _get_part_cnt(init_part, 100, 0)
    assert cnt == 5952


def test_get_part_cnt_last_term_limit():
    init_part = [1, 2, 3, 4, 15]
    cnt = _get_part_cnt(init_part, 25, 0, 9)
    assert cnt == 5

    #_init_part = get_init_partition(287, 12, 0, 2)
    # [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 210]

    # P(287, 12, 2) = 6267800603
    # too long ~23 mins
    #cnt = _get_part_cnt(_init_part, 287, 0)
    #assert cnt == 6267800603

    # P(287, 12, 2, 31) = 15
    # too long ~20 mins
    #cnt = _get_part_cnt(_init_part, 287, 0, 31)
    #assert cnt == 15

    _init_part = get_init_partition_ceil(287, 12, 0, 2, 31)
    cnt = _get_part_cnt(_init_part, 287, 0, 31)
    assert cnt == 15


def test_get_part_count_ceil():
    init_part = [1, 2, 3, 4, 5, 6, 29]
    _cnt = 0
    # count parts for term_idx = 0, iteration >= 3 where last term less than 13:
    _cnt3 = 0
    for p in gen_next_part(init_part, 50, 0, 50):
        if p[-1] < 13:
            _cnt += 1
            if p[0] >= 3:
                _cnt3 += 1

    assert _cnt == 39
    assert _cnt3 == 9
    # for all iterations:
    cnt = _get_part_cnt(init_part, 50, 0, 13)
    assert cnt == _cnt

    cnt = get_part_count_ceil(50, 7, 0, 1, 13)
    assert cnt == _cnt

    # for all iterations:
    cnt = get_part_count_ceil_by_prev_ceil(50, 7, 1, 13)
    assert cnt == _cnt

    # for iterations from 3 and above:
    cnt = get_part_count_ceil_by_prev_ceil(50, 7, 3, 13)
    assert cnt == _cnt3

    cnt = get_part_count_ceil_by_prev_ceil(27, 4, 3, 10)
    assert cnt == 3


def test_get_part_count_ceil_by_prev_ceil():
    cnt = get_part_count_ceil_by_prev_ceil(22, 4, 2, 13)
    assert cnt == 14

    cnt = get_part_count_ceil_by_prev_ceil(24, 4, 2, 12)
    assert cnt == 16


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

    cnt, is_stop = get_edge_partitions_by_term_iteration_cnt(50, 7, 0, 1)
    assert is_stop == False
    assert cnt == 60

    cnt, _ = get_edge_partitions_by_term_iteration_cnt(201, 5, 0, 1)
    assert cnt == 9987


def test_get_edge_partitions_by_term_iteration_cnt_diff():
    cnt_p_49_7 = 436
    cnt_p_50_7 = 522
    _diff = cnt_p_50_7 - cnt_p_49_7
    cnt = 0
    s = 50
    n = 7
    _min, _max = get_term_interval(s, n, 0)
    for j in range(_min, _max):
        _cnt, is_stop = get_edge_partitions_by_term_iteration_cnt(s, n, 0, j)
        cnt += _cnt
        if is_stop:
            break
    assert cnt == _diff  # 86


def test_get_term_iteration_max_part():
    _last = get_term_iteration_max_part(50, 7, 1, 5)
    assert _last == [1, 5, 6, 8, 9, 10, 11]


def test_get_max_partition():
    _last = get_max_partition(25, 5)
    assert _last == [3, 4, 5, 6, 7]

    _last = get_max_partition(100, 5)
    assert _last == [18, 19, 20, 21, 22]


def test_get_edge_partitions_by_term_iteration_cnt_play():
    #cnt, _ = get_edge_partitions_by_term_iteration_cnt(500, 20, 0, 1)
    #assert cnt == 9987
    pass


def test_tmp():
    init_part = [1, 2, 3, 21]
    _cnt = 0
    _cnt3 = 0
    cnt = 0
    print()
    for p in gen_next_part(init_part, 27, 0, 27):
        cnt += 1
        if p[-1] < 10:
            _cnt += 1
            if p[0] >= 3:
                print(p)
                _cnt3 += 1
    print(f"cnt: {_cnt}, cnt3: {_cnt3}, total: {cnt}")
