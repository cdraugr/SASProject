import csv
import typing as tp


def parse_links_from_json(filename: str) -> tp.List[str]:
    links: tp.List[str] = []
    with open(filename, 'r') as f:
        r = csv.reader(f)
        _ = next(r)

        for row in r:
            links.extend(row)

    return links
