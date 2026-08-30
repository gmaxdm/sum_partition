# sum_partition
Sum partition of distinct terms in ascending order.

Let Part(n, k) = q<sub>k</sub>(n) be the number of partitions of n into k parts.

# Strict partition function
A partition in which no part occurs more than once is called strict,
or is said to be a partition into distinct parts.
The function q(n) gives the number of these strict partitions of the given sum n.
For example, q(3) = 2 because the partitions 3 and 1 + 2 are strict,
while the third partition 1 + 1 + 1 of 3 has repeated parts.
q<sub>2</sub>(3) = 1 because only 1 + 2 partition is valid.

https://en.wikipedia.org/wiki/Partition_function_(number_theory)

Each strict partition can be presented in ascending order.

# k is fixed

It means partitions with k terms are valid only.
For example: Part(20, 5) = 7

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

Here idx is an index of term from which we start generate partitions
from min [1, 2, 3, 4, 10] to max [2, 3, 4, 5, 6].