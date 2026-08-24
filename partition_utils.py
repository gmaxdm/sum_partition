from typing import List, Tuple


def ap_sum(a: int, n: int) -> int:
    """
    a: first term
    n: number of terms
    """
    return (n * (2 * a + n - 1)) // 2


def is_valid(s: int, n: int, term_idx: int, iteration: int) -> bool:
    if s <= 0:
        return False
    if n < 2:
        return False
    return True


def get_ap_left_part_sum(term_idx: int, iteration: int, n: int) -> int:
    """
    get sum of a min (arithmetic progression) partition of term_idx and iteration (without the last item).
    this is the sum of two part: arithmetic progression before term_idx
    and arithmetic progression after the term_idx starting with iteration.
    :param term_idx:
    :param iteration:
    :param n:
    :return:
    """
    r_length = n - term_idx - 1
    return (1 + term_idx) * term_idx // 2 + (2 * iteration + r_length - 1) * r_length // 2


def get_tail_partition_iteration_cnt(s: int, left_part_sum: int, iteration: int, last_term_limit: int = -1) -> int:
    """
    partitions like: ... K[n-4] K+1[n-3] p2 p1, where n is terms number.
    :param s:
    :param left_part_sum:
    :param iteration: iteration is the n-3's term which is greater the n-4's term by 1.
    :param last_term_limit: limiter to the last term of the partition. It must be less than last_term_limit.
    :return:
    """
    if last_term_limit < 0:
        last_term_limit = 1 << 32

    _s = s - left_part_sum - iteration
    # get the first partition for this iteration
    p1_f = min(_s - iteration - 1, last_term_limit - 1)
    p2_f = _s - p1_f
    if p1_f <= p2_f:
        return 0

    # get the diff from the last partition for this iteration
    return p1_f - _s // 2


def get_init_partition(s: int, n: int, term_idx: int, iteration: int) -> List[int]:
    """
    Init a new partition for the term_idx index and iteration.
    :param s:
    :param n:
    :param term_idx:
    :param iteration:
    :return:
    """
    if s <= 0:
        raise ValueError("s should be positive")
    if n < 2:
        raise ValueError("term number should be at least 2")

    _part = [0] * n
    for i in range(term_idx):
        _part[i] = i + 1
    _part[term_idx] = iteration
    for i in range(1, n - term_idx):
        _part[term_idx + i] = iteration + i
    _part[-1] = s - get_ap_left_part_sum(term_idx, iteration, n)
    if _part[-1] <= _part[-2]:
        raise ValueError(f"can't create a new partition for term {term_idx} and iteration {iteration}")
    return _part


def get_partition_by_term_iteration_max_last(s: int, n: int, term_idx: int, iteration: int) -> List[int]:
    """
    max last tail partition in gen_next_part generator for the term_idx and iteration.
    Here idx is a term number from 0 to n - 1.
    :param s: sum
    :param n: number of terms
    :param term_idx: index
    :param iteration: term iteration from term min value to possible term max value
    :return:
    """
    if term_idx >= n-1:
        raise Exception("term index exceeds n")

    left_sum = ap_sum(1, term_idx) + iteration
    part = [0] * (term_idx+1)
    for i in range(term_idx):
        part[i] = i + 1
    part[term_idx] = iteration
    part.extend(get_partition_by_term_max_last(s-left_sum, n-term_idx-1, 0))
    return part


def get_partition_by_term_max_last(s: int, n: int, term_idx: int) -> List[int]:
    """
    max last tail partition in arithmetic progression for the term_idx.
    Here idx is a term number from 0 to n - 2.
    :param s: sum
    :param n: terms number
    :param term_idx: term's index
    :return:
    """
    if term_idx >= n-1:
        raise Exception("addend index exceeds n")

    _, _max = get_term_interval(s, n, term_idx)
    _part_ap_last = get_partition_by_term_iteration_ap_max_last(s, n, term_idx, _max)
    _diff = _part_ap_last[-2] - _part_ap_last[-3]
    if _diff == 1:
        return _part_ap_last
    # TODO: get the last max partition arithmetically:
    # ap max last
    # part = get_partition_by_term_iteration_ap_max_last(50, 7, 0, 1)
    # assert part == [1, 5, 6, 7, 8, 11, 12]

    # max last
    # part = get_partition_by_term_iteration_max_last(50, 7, 0, 1)
    # assert part == [1, 5, 6, 8, 9, 10, 11]
    return get_partition_by_term_iteration_ap_min_last(s, n, term_idx, _max)


def get_partition_by_term_ap_max_last(s: int, n: int, term_idx: int) -> List[int]:
    """
    max last tail partition in arithmetic progression for the term_idx.
    Here idx is a term number from 0 to n - 2.
    :param s: sum
    :param n: terms number
    :param term_idx: term's index
    :return:
    """
    if term_idx >= n-1:
        raise Exception("addend index exceeds n")

    _, _max = get_term_interval(s, n, term_idx)
    return get_partition_by_term_iteration_ap_min_last(s, n, term_idx, _max)


def get_partition_by_term_iteration_ap_max_last(s: int, n: int, term_idx: int, iteration: int) -> List[int]:
    """
    max last tail partition in arithmetic progression for the term_idx and iteration.
    Here idx is a term number from 0 to n - 1.
    :param s: sum
    :param n: number of terms
    :param term_idx: index
    :param iteration: term iteration from term min value to possible term max value
    :return:
    """
    if term_idx >= n-1:
        raise Exception("term index exceeds n")

    left_sum = ap_sum(1, term_idx) + iteration
    part = [0] * (term_idx+1)
    for i in range(term_idx):
        part[i] = i + 1
    part[term_idx] = iteration
    part.extend(get_partition_by_term_ap_max_last(s-left_sum, n-term_idx-1, 0))
    return part


def get_partition_by_term_iteration_ap_min_last(s: int, n: int, term_idx: int, iteration: int) -> List[int]:
    """
    last tail partition in arithmetic progression for the term_idx and iteration.
    :param s: sum
    :param n: terms number
    :param term_idx: term index
    :param iteration: term iteration from term min value to possible term max value
    :return:
    """
    if term_idx >= n-1:
        raise ValueError("term index exceeds n")
    _min, _max = get_term_interval(s, n, term_idx)
    if iteration < _min or iteration > _max:
        raise ValueError("term iteration exceeds iteration interval")

    part = [0] * n
    for i in range(term_idx):
        part[i] = i + 1
    part[term_idx] = iteration
    for i in range(1, n - term_idx):
        part[term_idx + i] = iteration + i
    left_sum = ap_sum(1, term_idx)

    if term_idx == n - 2:
        part[-1] = s - left_sum - iteration
    else:
        ap_sum_right = ap_sum(iteration, n - term_idx)
        _s = s - left_sum - ap_sum_right
        med = _s // 2
        part[-2] += med
        part[-1] += med
        if _s % 2 != 0:
            part[-1] += 1
    return part


def get_partition_by_term_iteration_ap_min_first(s: int, n: int, term_idx: int, iteration: int) -> List[int]:
    """
    first tail partition in the gen_next_part generator for the term_idx and iteration.
    :param s:
    :param n:
    :param term_idx:
    :param iteration:
    :return:
    """
    left_sum = ap_sum(1, term_idx)
    right_sum = ap_sum(iteration, n - term_idx - 1)
    p1 = s - left_sum - right_sum
    _part = [0] * n
    for i in range(term_idx):
        _part[i] = i + 1
    for i in range(n - term_idx - 1):
        _part[term_idx + i] = iteration + i
    _part[-1] = p1
    return _part


def get_partition_by_term_iteration_ap_min_last_term(s: int, n: int, term_idx: int, iteration: int) -> int:
    if term_idx >= n-1:
        raise Exception("term index exceeds n")
    _min, _max = get_term_interval(s, n, term_idx)
    if iteration < _min or iteration > _max:
        raise Exception("term iteration exceeds iteration interval")

    left_sum = ap_sum(1, term_idx)

    if term_idx == n - 2:
        return s - left_sum - iteration

    ap_sum_right = ap_sum(iteration, n - term_idx)
    _s = s - left_sum - ap_sum_right
    _last = n - term_idx - 1 + iteration
    med = _s // 2
    _last += med
    if _s % 2 != 0:
        _last += 1
    return _last


def get_term_interval(s: int, n: int, term_idx: int) -> Tuple[int, int]:
    """
    :param s:
    :param n:
    :param term_idx: term index from 0 to n-2 included
    :return:
    """
    k = term_idx
    _min = k + 1
    _max = (2*s - 2*k - 2*k*k - n*n + 2*n*k + n) // (2 * (n - k))
    return _min, _max


def get_partitions_cnt_by_term_iteration(s: int, n: int, term_idx: int, iteration: int) -> int:
    # first (min) partition for term idx and iteration:
    left_sum = ap_sum(1, term_idx)
    right_sum = ap_sum(iteration, n - term_idx - 1)
    p1 = s - left_sum - right_sum

    p2 = get_partition_by_term_iteration_ap_min_last_term(s, n, term_idx, iteration)
    return p1 - p2 + 1


