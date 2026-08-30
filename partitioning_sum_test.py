import pytest

from partitioning_sum import (sum_partitioning, sum_partition_cnt,
                              get_partitions_index_by_term_iteration,
                              get_partition_diff_by_searching, calc_sum_partitions_count_by_diff,
                              calc_sum_gen_partitions_count_by_diff)

PARAMS = [

]

@pytest.fixture(params=PARAMS)
def testcase(request):
    return request.param

def test_testcase(testcase):
    pass


def test_sum_partitioning():
    parts = sum_partitioning(15, 5)
    assert len(parts) == 1
    assert parts == [[1, 2, 3, 4, 5]]

    parts = sum_partitioning(20, 5)
    assert len(parts) == 7
    assert parts[-1] == [1, 2, 3, 4, 10]
    print(parts)


def test_get_partition_diff_by_searching_low_sum():
    parts = get_partition_diff_by_searching(15, 5)
    assert len(parts) == 1
    parts = get_partition_diff_by_searching(16, 5)
    assert len(parts) == 0
    parts = get_partition_diff_by_searching(17, 5)
    assert len(parts) == 1
    parts = get_partition_diff_by_searching(18, 5)
    assert len(parts) == 1
    parts = get_partition_diff_by_searching(19, 5)
    assert len(parts) == 2
    parts = get_partition_diff_by_searching(20, 5)
    assert len(parts) == 2


def test_get_partition_diff_by_searching():
    parts = get_partition_diff_by_searching(21, 5)
    res = [
        [1, 3, 4, 6, 7],
        [1, 2, 5, 6, 7],
        [1, 2, 3, 7, 8],
    ]
    assert parts == res

    parts = get_partition_diff_by_searching(25, 5)
    assert len(parts) == 7

    parts = get_partition_diff_by_searching(57, 10)
    res = [
        [1, 2, 3, 4, 5, 6, 7, 8, 10, 11],
    ]
    assert parts == res

    parts = get_partition_diff_by_searching(101, 5)
    assert len(parts) == 1118

    #parts = get_partition_diff_by_searching(5001, 10)
    #assert len(parts) == 5118
    #parts = get_partition_diff_by_searching(5002, 10)
    #assert len(parts) == 1948

    #parts = get_partition_diff_by_searching(20481, 10)
    #assert len(parts) == 21145

    #parts = get_partition_diff_by_searching(102, 5)
    #print(len(parts))


def test_calc_sum_gen_partitions_count_by_diff():
    cnt = calc_sum_gen_partitions_count_by_diff(100, 101, 25337, 5)
    assert cnt == 26455

    cnt = calc_sum_gen_partitions_count_by_diff(210, 250, 1, 20)
    assert cnt == 35251

    #cnt = calc_sum_gen_partitions_count_by_diff(250, 300, 35251, 20)
    #assert cnt == 33114319


def test_sum_partition_cnt():
    cnt = sum_partition_cnt(210, 20)
    assert cnt == 1

    cnt = sum_partition_cnt(250, 20)
    assert cnt == 35251


def test_calc_sum_partitions_count():
    #cnt = calc_sum_partitions_count_by_diff(100, 101, 25337, 5)
    #assert cnt == 26455

    cnt = calc_sum_partitions_count_by_diff(210, 250, 1, 20)
    assert cnt == 35251

    #cnt = calc_sum_partitions_count_by_diff(250, 300, 35251, 20)
    #assert cnt == 33114319  # ok

    #cnt = calc_sum_partitions_count_by_diff(250, 300, 991440410, 10)
    #assert cnt == 6194373023  # ok


def test_get_partitions_index_by_term_iteration():
    #idx = get_partitions_index_by_term_iteration(25, 5, 2, 4, 11)
    #assert idx == 13

    #idx = get_partitions_index_by_term_iteration(25, 5, 2, 5, 10)
    #assert idx == 16

    idx = get_partitions_index_by_term_iteration(23, 5, 3, 7, 10)
    assert idx == 14


#def test_save_sum_partitions():
    #save_sum_partitions(250, 20, save_csv=True)
