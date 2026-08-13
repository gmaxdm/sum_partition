import pytest

from compression_utils import (gen_ordered_numbers, compress_layer, decompress_layer, check_csv_file_with_partitions,
                               split_by_layers, ints_to_bytes, layers_to_bytes, NUM_LEN)


def test_ordered_numbers_compress_decompress_layer():
    nums = gen_ordered_numbers(NUM_LEN)
    compressed = compress_layer(nums)
    decompressed = decompress_layer(compressed)
    assert nums == decompressed


def test_ints_to_bytes():
    nums = [1, 1024, 1048575]
    bytes_list = ints_to_bytes(nums)
    res = [0, 0, 0, 1, 0, 0, 4, 0, 0, 15, 255, 255]
    assert bytes_list == res


def test_split_by_layers():
    nums = [1, 2, 1, 3, 4, 4, 1, 3]
    layers = split_by_layers(nums)
    bytes_list = layers_to_bytes(layers, len(nums))
    assert nums == bytes_list

def test_check_csv_file_with_partitions():
    res = check_csv_file_with_partitions("sum_partition/csv/250_20.csv")
    assert res.no_duplicates == True
    assert res.every_sum_is_correct == True
    assert res.no_duplicates_in_terms == True
    assert res.ascending_order == True