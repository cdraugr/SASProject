import pandas as pd
from tqdm import tqdm

from srcs.text_analytics import get_all_by_link


def main():
    pd.DataFrame(
        [get_all_by_link(link) for link in tqdm(pd.read_csv('links.csv')['link'])]
    ).to_csv('data.csv', index=False)


if __name__ == '__main__':
    main()
