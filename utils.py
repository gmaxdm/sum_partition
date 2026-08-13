import csv

from typing import List


def save_to_csv(filename: str, data: List[List[int]]) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data)