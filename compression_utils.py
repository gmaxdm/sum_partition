import random
import zlib
import lzma
import os

from typing import List

NUM_LEN = 2048
MAX_INT = 256


def gen_bytes(length: int) -> List[int]:
    nums = []
    for i in range(length):
        num = random.randint(0, MAX_INT-1)
        nums.append(num)
    return nums


def split_by_layers(nums: List[int]) -> List[List[int]]:
    m = [[]] * 256
    for i, v in enumerate(nums):
        # since the list is mutable, the upper format creates the same reference to all 256 lists,
        # we need to create a new reference to the concrete list.
        if not m[v]:
            m[v] = []
        m[v].append(i+1)
    return m


def layers_to_bytes(layers: List[List[int]], length: int) -> List[int]:
    bytes_list = [0] * length
    for i, layer in enumerate(layers):
        for idx in layer:
            bytes_list[idx-1] = i
    return bytes_list


def ints_to_bytes(nums: List[int]) -> List[int]:
    """
    returns a list of byte integers (0-256). Each integer is represented as 4 integers in big endian
    :param nums:
    :return:
    """
    bytes_list = []
    for v in nums:
        for i in list(bytearray(v.to_bytes(4, byteorder='big'))):
            bytes_list.append(i)
    return bytes_list


def gen_ordered_numbers(length: int) -> List[int]:
    nums = set()
    for i in range(length):
        num = random.randint(1, MAX_INT)
        nums.add(num)
    return sorted(nums)


def compress_layer(nums: List[int], method: str = "ZLIB") -> List[int]:
    """
    :param nums: list of integers that are distinct and sorted in ascending order
    :param method: ZLIB
    :return: compressed list of integers in the following structure:
            [0: first diff (big 4 bytes integer), 1... compressed data]
    """
    diffs = []
    for i in range(len(nums) - 1):
        diffs.append(nums[i + 1] - nums[i])
    #print(nums)
    #print(diffs)
    if method == "LZMA":
        cmethod = lzma.compress
    else:
        cmethod = zlib.compress

    compressed_diffs = cmethod(bytes(ints_to_bytes(diffs)))
    lt = ints_to_bytes([nums[0]]) + list(compressed_diffs)
    #print(lt)
    return lt


def decompress_layer(nums: List[int], method: str = "ZLIB") -> List[int]:
    if method == "LZMA":
        cmethod = lzma.decompress
    else:
        cmethod = zlib.decompress
    decompressed_diffs = cmethod(bytes(nums[4:]))
    prev = int.from_bytes(nums[:4], byteorder='big', signed=False)
    original_nums = [prev]
    data = list(decompressed_diffs)
    for v in (data[i:i+4] for i in range(0, len(data), 4)):
        prev += int.from_bytes(v, byteorder='big', signed=False)
        original_nums.append(prev)
    return original_nums


def print_layers_stat(layers: List[List[int]]) -> int:
    """
    Need sum partitioning with 10 - 20 addends that fits 2 byte size.
    Sums: approx. 10*NUM_LEN - 20*NUM_LEN
    The question: what size does the partitioning index fit?
    :param layers:
    :return: predict size
    """
    predict_size = 256 * 6
    layers_len = 0
    mx = 0
    mn = MAX_INT
    avg = 0
    gt_6_bytes = 0
    max_cnt_len = 0
    len_cnt = {}
    for i, layer in enumerate(layers):
        if not layer:
            continue

        layers_len += 1
        l = len(layer)
        if l > mx:
            mx = l
        if l < mn:
            mn = l
        avg += l
        if l > 6:
            gt_6_bytes += 1
        try:
            len_cnt[l] += 1
        except KeyError:
            len_cnt[l] = 1
    avg //= layers_len
    print("Using 2 bytes for sum and 4 bytes for partition index.")
    print("Need sum partitioning with 10 - 20 addends that fits 4 byte size.")
    print(f"Sums: approx. {10 * NUM_LEN} - {20 * NUM_LEN}")
    print("The question: what size does the partitioning index fit?")
    print("After the diff method calculations:")
    print("P(20480, 10) - 149022445")
    print("P(40960, 10) - 597720139")
    print("P(20480, 20) - 215431794")
    print("P(40960, 20) - 870767890")
    print("layers len", layers_len)
    print("layers length cnt", sorted([(k, v) for k, v in len_cnt.items()], reverse=True))
    print(f"max: {mx}, min: {mn}, avg: {avg}, gt_6_bytes: {gt_6_bytes}")
    print(f"max sum: {mx * NUM_LEN}, fits 2 bytes size ({2**16}): {mx * NUM_LEN < 2**16}")
    print(f"predictable size: {predict_size / 1024:.2f} KB")
    #print([len(v) for v in layers.values()])
    return predict_size


class CheckCSVResult:
    every_sum_is_correct = False
    no_duplicates = False
    ascending_order = False
    no_duplicates_in_terms = False


def check_csv_file_with_partitions(csv: str) -> CheckCSVResult:
    """
    :param csv:
    :return:
    """
    res = CheckCSVResult()
    filename = os.path.join(os.getcwd(), csv)
    size = os.path.getsize(filename)
    if size > 3*1024*1024:
        print("csv file is too big")
        return res

    with open(filename, "r") as f:
        lines = f.readlines()
        parts = []
        for line in lines:
            part = tuple(map(int, line.split(",")))
            parts.append(part)

        if not parts:
            print("no parts")
            return res

        cnt = len(parts)
        s = sum(parts[0])
        n = len(parts[0])
        print(f"Count: {cnt}")
        print(f"Sum: {s}")
        print(f"N: {n}")
        print()

        # check for duplicates and sum
        res.every_sum_is_correct = True
        res.no_duplicates = True
        res.ascending_order = True
        res.no_duplicates_in_terms = True

        parts_set = set()
        for part in parts:
            _s = sum(part)
            if _s != s:
                print(f"sum is different: {_s}", part)
                res.every_sum_is_correct = False
            parts_set.add(part)

            _term_set = set()
            prev = 0
            for term in part:
                _term_set.add(term)
                if term <= prev:
                    print("ascending order is failed", part)
                    res.ascending_order = False
            if len(_term_set) != n:
                print("part has duplicate terms", part)
                res.no_duplicates_in_terms = False
        if len(parts_set) != cnt:
            res.no_duplicates = False

    return res

