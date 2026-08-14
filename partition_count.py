import copy

from typing import List, Generator, Tuple

from mongo.client import MongoDBClient as mongo
from partition_utils import (ap_sum, get_init_partition, get_term_iteration_interval,
                             get_partition_by_term_iteration_ap_min_last,
                             get_partition_by_term_iteration_ap_max_last,
                             get_tail_partition_iteration_cnt)


class SmallLengthPartitionsStopIteration(Exception):
    pass


def get_part_cnt(init_part: List[int], s: int, idx: int, last_term_limit: int = 0) -> int:
    """
    increment the most right term n-1 (before the result sum term - last),
    when the rule is failed increment n-2 by creating the min partition for this iteration
    and so on till the most left term and its all iterations.
    1, 2, 3, 4, 15
    starting with:
        term_idx = n-4 (2)
        iteration = 3
        left_part_sum = 3
        get_tail_partition_iteration_cnt(25, 3, 3) = 6

    Caching in part_ceil by (s, n, i, c), where i - iteration = init_part[0], c - ceil = last_term_limit.
    :param init_part: initial partition
    :param s: sum
    :param idx: term_idx from 0 to n-4
    :param last_term_limit: limiter to the last term of the partition that is being generated.
                            Last term < last_term_limit.
    :return:
    """
    n = len(init_part)
    if n < 2:
        raise ValueError("n is too small")
    if idx > n - 4:
        raise ValueError("idx should be less than n-4")

    init_iteration = init_part[0]
    ceil = last_term_limit
    if last_term_limit > 0:
        cnt = mongo.get_part_ceil(s, n, init_iteration, last_term_limit)
        if cnt >= 0:
            print(f"P({s}, {n}, {init_iteration}, {last_term_limit}) = {cnt} (getting from cache)")
            return cnt
    else:
        ceil = 1 << 32

    part = init_part
    term_idx = n - 4
    # keep the left sum before term_idx
    left_part_sum = 0
    for i in range(term_idx):
        left_part_sum += part[i]

    _, _max = get_term_iteration_interval(s, n, term_idx + 1)
    iteration = part[term_idx + 1]
    cnt = 0
    _cnt = 0
    is_valid = part[-2] < part[-1]
    while True:
        if is_valid:
            _cnt = get_tail_partition_iteration_cnt(s, left_part_sum + part[term_idx], iteration,
                                                    last_term_limit=ceil)
        if _cnt or iteration <= _max:
            # n-3
            cnt += _cnt
            iteration += 1
        else:
            part[term_idx] += 1
            for i in range(1, n - term_idx):
                part[term_idx + i] = part[term_idx] + i
            part[-1] = s - ap_sum(part[term_idx], n - term_idx - 1) - left_part_sum
            if part[-2] < part[-1]:
                for i in range(term_idx, n - 4):
                    left_part_sum += part[i]
                term_idx = n - 4
                iteration = part[term_idx + 1]
                is_valid = True
            else:
                term_idx -= 1
                if term_idx < idx:
                    break
                left_part_sum -= part[term_idx]
                # reset values:
                is_valid = False
                _cnt = 0

    if last_term_limit > 0:
        mongo.add_part_ceil(s, n, init_iteration, last_term_limit, cnt)
        print(f"P({s}, {n}, {init_iteration}, {last_term_limit}) = {cnt}")

    return cnt


def get_part_cnt_error(s: int, n: int, idx: int, last_term_limit: int) -> int:
    """
    increment the most right term n-1 (before the result sum term - last),
    when the rule is failed increment n-2 by creating the min partition for this iteration
    and so on till the most left term and its all iterations.
    1, 2, 3, 4, 15
    starting with:
        term_idx = n-3 (2)
        iteration = 3
        left_part_sum = 3
        get_tail_partition_iteration_cnt(25, 3, 3) = 6
    :param s: sum
    :param n: terms number
    :param idx: term_idx from 0 to n-2
    :param last_term_limit: limiter to the last term of the partition that is being generated.
    :return:
    """
    term_idx = n - 4
    # keep the left sum before term_idx
    left_part_sum = ap_sum(1, term_idx+1)
    iteration = term_idx + 2
    i = iteration
    lps = 0
    ti = term_idx
    is_tail = False
    cnt = 0
    is_valid = True
    while True:
        _cnt = get_tail_partition_iteration_cnt(s, left_part_sum + lps, i)
        if _cnt:
            # n-3
            cnt += _cnt
            i += 1
            is_tail = True
        else:
            if is_tail:
                # n-4
                # part[term_idx]++
                lps += 1
                iteration += 1
                i = iteration
                is_tail = False
                ti = n - 4
            else:
                # term_idx--
                if ti == term_idx:
                    term_idx -= 1
                    if term_idx < idx:
                        break
                ti -= 1
                left_part_sum -= lps
                left_part_sum += 2
                # term_idx = n-4
                #lps = left_part_sum + ap_sum(term_idx + 3, n - 4 - term_idx)
                lps = 0
                is_tail = True
                i = s  # _cnt = 0
                # iteration = part[n-3]
                iteration = n - 1 - term_idx
    return cnt


def gen_next_part_old(init_part: List[int], s: int, idx: int, last_term_limit: int) -> Generator:
    """
    Generating partitions by the method:
    increment the most right term n-1 (before the result sum term - last),
    when the rule is failed increment n-2 by creating the min partition for this iteration
    and so on till the most left term and its all iterations.
    :param init_part: initial partition
    :param s: sum
    :param idx: term_idx from 0 to n-2
    :param last_term_limit: limiter to the last term of the partition that is being generated.
    :return:
    """
    n = len(init_part)
    part = init_part

    # we still can generate some valid partitions for term_idx+1 and more even when last_term_limit <= part[-1].
    #if last_term_limit <= part[-1]:
    #    return

    term_idx = n - 2
    # keep the left sum before term_idx
    left_part_sum = 0
    for i in range(term_idx):
        left_part_sum += part[i]

    p2 = part[-2]
    p1 = part[-1]
    while True:
    #for j in range(30):
        if p2 < p1 < last_term_limit:
            part[-2] = p2
            part[-1] = p1
            yield part
            part = copy.copy(part)
            p2 += 1
            p1 -= 1
        else:
            part[term_idx] += 1
            for i in range(1, n - term_idx):
                part[term_idx + i] = part[term_idx] + i
            part[-1] = s - ap_sum(part[term_idx], n - term_idx - 1) - left_part_sum
            #print(ap_sum(part[term_idx], n - term_idx - 1), left_part_sum)
            #print("init ", part)
            p2 = part[-2]
            p1 = part[-1]
            if p2 < p1 < last_term_limit:
                for i in range(term_idx, n - 3):
                    left_part_sum += part[i]
                #print("term_idx = n-3: left_part_sum:", left_part_sum)
                term_idx = n - 3
            else:
                term_idx -= 1
                left_part_sum -= part[term_idx]
                #print("term_idx -= 1: left_part_sum:", left_part_sum)
                if term_idx < idx:
                    break

def gen_next_part(init_part: List[int], s: int, idx: int, last_term_limit: int) -> Generator:
    """
    Generating partitions by the method:
    increment the most right term n-1 (before the result sum term - last),
    when the rule is failed increment n-2 by creating the min partition for this iteration
    and so on till the most left term and its all iterations.
    :param init_part: initial partition
    :param s: sum
    :param idx: term_idx from 0 to n-2
    :param last_term_limit: limiter to the last term of the partition that is being generated.
    :return:
    """
    n = len(init_part)
    part = init_part

    # we still can generate some valid partitions for term_idx+1 and more even when last_term_limit <= part[-1].
    #if last_term_limit <= part[-1]:
    #    return

    term_idx = n - 2
    # keep the left sum before term_idx
    left_part_sum = 0
    for i in range(term_idx):
        left_part_sum += part[i]

    is_valid = part[-2] < part[-1] < last_term_limit
    while True:
    #for j in range(30):
        if is_valid:
            yield part
        part = copy.copy(part)
        part[term_idx] += 1
        for i in range(1, n - term_idx):
            part[term_idx + i] = part[term_idx] + i
        part[-1] = s - ap_sum(part[term_idx], n - term_idx - 1) - left_part_sum
        #print(ap_sum(part[term_idx], n - term_idx - 1), left_part_sum)
        #print("init ", part)
        if part[-2] < part[-1]:
            for i in range(term_idx, n - 2):
                left_part_sum += part[i]
            #print("term_idx = n-2: left_part_sum:", left_part_sum)
            term_idx = n - 2
            is_valid = part[-1] < last_term_limit
        else:
            term_idx -= 1
            if term_idx < idx:
                break
            left_part_sum -= part[term_idx]
            #print("term_idx -= 1: left_part_sum:", left_part_sum)
            is_valid = False


def gen_next_part_error(init_part: List[int], idx: int, s: int) -> Generator:
    """
    -- generating edge partitions --
    We are working with one idx index of a row.
        idx - addend which is growing.
    We are transforming the partitioning by decreasing the most right addend by 1
    and increasing the previous addend by 1, so the sum is the same.
    When the distinct and ascended order rule is failed we increase the next term by 1.
    When we reach the last possible partition for this idx we stop.
    """
    n = len(init_part)
    part = init_part
    iteration = part[idx]
    p2 = part[-2]
    p1 = part[-1]
    while True:
        if p2 < p1:
            part[-2] = p2
            part[-1] = p1
            yield part
            part = copy.copy(part)
            p2 += 1
            p1 -= 1
        else:
            # the idea is to generate the partitions recursively.
            # for example, P(20, 5) is
            # the above partitions and
            # nested partitions for P(18, 4) and so on
            # see nested formula
            try:
                iteration += 1
                part = get_init_partition(s, n, idx, iteration)
            except ValueError:
                break


def gen_edge_partitions_by_term_iteration(s: int, n: int, term_idx: int, iteration: int) -> Generator:
    """
    edge partition: p[-1] - p[-2] == 1
    :param s:
    :param n:
    :param term_idx:
    :param iteration:
    :return:
    """
    if term_idx >= n - 1:
        raise Exception("term index exceeds n - 1")

    _min, _max = get_term_iteration_interval(s, n, term_idx + 1)
    left_sum = ap_sum(1, term_idx)
    middle_terms_cnt = n - term_idx - 3
    if middle_terms_cnt < 3:
        # Below we use the attributes partitions with more than 5 terms like last two terms sum.
        # partitions with less than 5 terms is a special case:
        _s = s - left_sum
        try:
            _init_part = get_init_partition(_s, n - term_idx, 0, iteration)
        except ValueError:
            return

        for _part in gen_next_part(_init_part, _s, 0, _s):
            if _part[-1] - _part[-2] == 1:
                yield [*range(1, term_idx+1), *_part]
        raise SmallLengthPartitionsStopIteration

    #ap_offset = iteration - term_idx - 1
    #for i in range(term_idx+1,n-2):
    #    _min, _max = get_term_iteration_interval(s, n, i)
    #    _min += ap_offset
    #    print(_min, _max)

    left_sum += iteration
    _left_part = [0] * (term_idx + 1)
    for i in range(term_idx):
        _left_part[i] = i + 1
    _left_part[term_idx] = iteration

    _part_first = get_partition_by_term_iteration_ap_min_last(s, n, term_idx, iteration)
    _part_last = get_partition_by_term_iteration_ap_max_last(s, n, term_idx, iteration)
    #print(_part_first)
    #print(_part_last)

    _sum_max = _part_first[-1] + _part_first[-2]
    _sum_min = _part_last[-1] + _part_last[-2]
    # now we are looking the last max partition for term_idx by gen_max_part
    # need to use get_partition_by_term_iteration_max_last(s, n, term_idx, iteration) instead
    for _part in gen_next_part(_part_last, s, term_idx+1, s):
        #print("gen part:", _part)
        _sum_min_gen = _part[-1] + _part[-2]
        if _sum_min_gen < _sum_min:
            _sum_min = _sum_min_gen

    _part = _part_first
    _sum = _sum_max
    while _sum >= _sum_min:
        if _sum % 2 == 0:
            _sum -= 1
            continue

        _s = s - left_sum - _sum
        try:
            _init_part = get_init_partition(_s, middle_terms_cnt, 0, iteration+1)
            #print(f"init {_s}:", _init_part)
        except ValueError:
            _sum -= 1
            continue

        med = _sum // 2
        p2 = med
        p1 = med + 1

        for _p in gen_next_part(_init_part, _s, 0, p2):
            _part = copy.copy(_left_part)
            _part.extend(_p)
            _part.append(p2)
            _part.append(p1)
            yield _part
        _sum -= 1


def get_edge_partitions_by_term_iteration_cnt(s: int, n: int, term_idx: int, iteration: int) -> int:
    """
    edge partition: p[-1] - p[-2] == 1
    :param s:
    :param n:
    :param term_idx:
    :param iteration:
    :return:
    """
    if term_idx >= n - 1:
        raise Exception("term index exceeds n - 1")

    cnt = 0

    _min, _max = get_term_iteration_interval(s, n, term_idx + 1)
    left_sum = ap_sum(1, term_idx)
    middle_terms_cnt = n - term_idx - 3
    if middle_terms_cnt < 3:
        # Below we use the attributes partitions with more than 5 terms like last two terms sum.
        # partitions with less than 5 terms is a special case:
        _s = s - left_sum
        try:
            _init_part = get_init_partition(_s, n - term_idx, 0, iteration)
        except ValueError:
            return cnt

        for _part in gen_next_part(_init_part, _s, 0, _s):
            if _part[-1] - _part[-2] == 1:
                cnt += 1
        raise SmallLengthPartitionsStopIteration(cnt)

    left_sum += iteration

    _part_first = get_partition_by_term_iteration_ap_min_last(s, n, term_idx, iteration)
    _part_last = get_partition_by_term_iteration_ap_max_last(s, n, term_idx, iteration)

    _sum_max = _part_first[-1] + _part_first[-2]
    _sum_min = _part_last[-1] + _part_last[-2]
    # now we are looking the last max partition for term_idx by gen_max_part
    # need to use get_partition_by_term_iteration_max_last(s, n, term_idx, iteration) instead
    for _part in gen_next_part(_part_last, s, term_idx + 1, s):
        # print("gen part:", _part)
        _sum_min_gen = _part[-1] + _part[-2]
        if _sum_min_gen < _sum_min:
            _sum_min = _sum_min_gen

    _sum = _sum_max
    while _sum >= _sum_min:
        if _sum % 2 == 0:
            _sum -= 1
            continue

        _s = s - left_sum - _sum
        try:
            _init_part = get_init_partition(_s, middle_terms_cnt, 0, iteration+1)
        except ValueError:
            _sum -= 1
            continue

        med = _sum // 2
        cnt += get_part_cnt(_init_part, _s, 0, med)
        _sum -= 1

    return cnt


def get_edge_partitions_by_term_iteration_cnt(s: int, n: int, term_idx: int, iteration: int) -> Tuple[int, bool]:
    """
    "E({s}, {n}, {term_idx}, {iteration}) = {cnt}"
    :param s:
    :param n:
    :param term_idx:
    :param iteration:
    :return:
    """
    _cnt = 0
    is_stop = False
    try:
        _cnt = _get_edge_partitions_by_term_iteration_cnt(s, n, term_idx, iteration)
    except SmallLengthPartitionsStopIteration as e:
        _cnt = e.args[0]
        is_stop = True
    return _cnt, is_stop

