import csv


def read_annotations(path):
    with open(path, newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))
