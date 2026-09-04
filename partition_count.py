import copy
import logging

from typing import List, Generator, Tuple

from mongo.client import get_client
from bench import BenchmarkTags
from partition_utils import (ap_sum, get_init_partition, get_term_interval,
                             get_partition_by_term_iteration_ap_min_last,
                             get_partition_by_term_iteration_ap_max_last,
                             get_tail_partition_iteration_cnt, get_min_part_last_term,
                             is_partition_valid, get_init_partition_ceil)


logger = logging.getLogger('partition')


class SmallLengthPartitionsStopIteration(Exception):
    pass


@BenchmarkTags(tags="PC")
def _get_part_cnt(init_part: List[int], s: int, idx: int, last_term_limit: int = 0) -> int:
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
    if n < 4:
        cnt = 0
        for _ in gen_next_part(init_part, s, idx, last_term_limit):
            cnt += 1
        return cnt

    _mongo = get_client()

    init_iteration = init_part[0]
    ceil = last_term_limit
    # See the get_part_count_ceil for ceil validation.
    # It is supposed that the ceil is used by get_part_count_ceil only.
    if last_term_limit > 0:
        cnt = _mongo.get_part_ceil(s, n, init_iteration, last_term_limit)
        if cnt:
            logger.info(f"P({s}, {n}, {init_iteration}, {last_term_limit}) = {cnt} (getting from cache)")
            return cnt
    else:
        # some big integer like 1 << 32:
        ceil = s

    part = init_part
    # to log correct init_part use:
    # part = init_part[:]
    term_idx = n - 4
    # keep the left sum before term_idx
    left_part_sum = 0
    for i in range(term_idx):
        left_part_sum += part[i]

    _, _max = get_term_interval(s, n, term_idx + 1)
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
        _mongo.add_part_ceil(s, n, init_iteration, last_term_limit, cnt)
        logger.info(f"P({s}, {n}, {init_iteration}, {last_term_limit}) = {cnt}")

    return cnt


def get_part_count(s: int, n: int, term_idx: int, iteration: int) -> int:
    """ returns all partitions for term_idx starting from iteration.
    """
    cnt = 0
    try:
        _init_part = get_init_partition(s, n, term_idx, iteration)
    except ValueError:
        return cnt

    return _get_part_cnt(_init_part, s, term_idx)


def get_part_count_ceil(s: int, n: int, term_idx: int, iteration: int, ceil: int) -> int:
    """ returns all partitions for term_idx starting from iteration using ceil.
    """
    cnt = 0
    try:
        _init_part = get_init_partition_ceil(s, n, term_idx, iteration, ceil)
        #_init_part = get_init_partition(s, n, term_idx, iteration)
    except ValueError:
        return cnt

    return _get_part_cnt(_init_part, s, term_idx, ceil)


def get_part_count_ceil_by_prev_ceil(s: int, n: int, iteration: int, ceil: int) -> int:
    """
    P(S, n, i, c) = P(S, n, i, c-1) + P(S-c+1,n-1,i,c-1)
    term_idx = 0, it means we count partitions for the iteration of the first term.
    """
    if not is_partition_valid(s, n, 0, iteration):
        return 0

    if ceil < n:
        raise Exception(f"so small ceil is not expected: P({s}, {n}, {iteration}, {ceil})")

    _max_ceil = get_min_part_last_term(s, n, iteration)

    if ceil > _max_ceil:
        return get_part_count(s, n, 0, iteration)

    _mongo = get_client()

    cnt = _mongo.get_part_ceil(s, n, iteration, ceil)
    if cnt:
        logger.info(f"P({s}, {n}, {iteration}, {ceil}) = {cnt} (getting from cache)")
        return cnt

    _cnt = get_part_count_ceil(s, n, 0, iteration, ceil-1)
    _cnt += get_part_count_ceil(s - ceil + 1, n-1, 0, iteration, ceil-1)

    if _cnt:
        _mongo.add_part_ceil(s, n, iteration, ceil, _cnt)
        logger.info(f"P({s}, {n}, {iteration}, {ceil}) = {_cnt}")
    return _cnt


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
        #logger.info(ap_sum(part[term_idx], n - term_idx - 1), left_part_sum)
        #logger.info("init ", part)
        if part[-2] < part[-1]:
            for i in range(term_idx, n - 2):
                left_part_sum += part[i]
            #logger.info("term_idx = n-2: left_part_sum:", left_part_sum)
            term_idx = n - 2
            is_valid = part[-1] < last_term_limit
        else:
            term_idx -= 1
            if term_idx < idx:
                break
            left_part_sum -= part[term_idx]
            #logger.info("term_idx -= 1: left_part_sum:", left_part_sum)
            is_valid = False


def get_term_iteration_max_part(s: int, n: int, term_idx: int, iteration: int)-> List[int]:
    _part_first = get_partition_by_term_iteration_ap_min_last(s, n, term_idx, iteration)
    _part_last = get_partition_by_term_iteration_ap_max_last(s, n, term_idx, iteration)

    _last = _part_last
    for _part in gen_next_part(_part_last, s, term_idx + 1, s):
        _last = _part
    return _last


def get_max_partition(s: int, n: int) -> List[int]:
    _min, _max = get_term_interval(s, n, 0)
    return get_term_iteration_max_part(s, n, 0, _max)


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

    _min, _max = get_term_interval(s, n, term_idx + 1)
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
    #    _min, _max = get_term_interval(s, n, i)
    #    _min += ap_offset
    #    logger.info(_min, _max)

    left_sum += iteration
    _left_part = [0] * (term_idx + 1)
    for i in range(term_idx):
        _left_part[i] = i + 1
    _left_part[term_idx] = iteration

    _part_first = get_partition_by_term_iteration_ap_min_last(s, n, term_idx, iteration)
    _part_last = get_partition_by_term_iteration_ap_max_last(s, n, term_idx, iteration)
    #logger.info(_part_first)
    #logger.info(_part_last)

    _sum_max = _part_first[-1] + _part_first[-2]
    _sum_min = _part_last[-1] + _part_last[-2]
    # now we are looking the last max partition for term_idx by gen_next_part
    # need to use get_partition_by_term_iteration_max_last(s, n, term_idx, iteration) instead
    for _part in gen_next_part(_part_last, s, term_idx+1, s):
        #logger.info("gen part:", _part)
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
            #logger.info(f"init {_s}:", _init_part)
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


def _get_edge_partitions_by_term_iteration_cnt(s: int, n: int, term_idx: int, iteration: int) -> int:
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

    _min, _max = get_term_interval(s, n, term_idx + 1)
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
    # now we are looking the last max partition for term_idx by gen_next_part
    # need to use get_partition_by_term_iteration_max_last(s, n, term_idx, iteration) instead
    for _part in gen_next_part(_part_last, s, term_idx + 1, s):
        # logger.info("gen part:", _part)
        _sum_min_gen = _part[-1] + _part[-2]
        if _sum_min_gen < _sum_min:
            _sum_min = _sum_min_gen

    #print("----------------------------")
    #print("sum: ", _sum_min, _sum_max)
    _sum = _sum_max
    while _sum >= _sum_min:
        if _sum % 2 == 0:
            _sum -= 1
            continue

        _s = s - left_sum - _sum
        med = _sum // 2
        #__cnt = get_part_count_ceil(_s, middle_terms_cnt, iteration+1, med)
        #__cnt = get_part_count(_s, middle_terms_cnt, 0, iteration+1, med)
        __cnt = get_part_count_ceil_by_prev_ceil(_s, middle_terms_cnt, iteration+1, med)
        #print(f"calc P({_s}, {middle_terms_cnt}, {iteration+1}, {med}) = {__cnt}")
        cnt += __cnt
        #cnt += get_part_count(_s, middle_terms_cnt, 0, iteration+1, med)
        _sum -= 1

    return cnt


@BenchmarkTags(tags="E")
def get_edge_partitions_by_term_iteration_cnt(s: int, n: int, term_idx: int, iteration: int) -> Tuple[int, bool]:
    """
    "E({s}, {n}, {term_idx}, {iteration}) = {cnt}"
    :param s:
    :param n:
    :param term_idx:
    :param iteration:
    :return:
    """
    is_stop = False
    _mongo = get_client()
    if term_idx == 0:
        _cnt = _mongo.get_edge(s, n, iteration)
        if _cnt:
            logger.info(f"E({s}, {n}, 0, {iteration}) = {_cnt} (getting from cache)")
            return _cnt, is_stop

    try:
        _cnt = _get_edge_partitions_by_term_iteration_cnt(s, n, term_idx, iteration)
    except SmallLengthPartitionsStopIteration as e:
        _cnt = e.args[0]
        is_stop = True

    if term_idx == 0:
        _mongo.add_edge(s, n, iteration, _cnt)
        logger.info(f"E({s}, {n}, 0, {iteration}) = {_cnt}")
    return _cnt, is_stop

