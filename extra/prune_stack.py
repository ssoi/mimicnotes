'''Prune the stack exchange dataset to contain questions with length >= 100 words.'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import bs4
import csv
from multiprocessing import Pool
from pathlib import Path
import re


data_dir = '../data/stack/data'
out_dir = '../data/stack'
cpus = 7


alpha_re = re.compile(r"^[\sa-z0-9?.,-:]+$")


def process_text(rows):
    ret = []
    for i, row in enumerate(rows):
        body = row[-1]
        soup = bs4.BeautifulSoup(body, 'lxml')
        for code in soup.find_all('code'):
            code.clear()
        text = soup.text
        if i % 5000 == 0:
            print(i, i*100 / len(rows))
        length = len(text.split())
        if length < 100:  # skip questions shorter than 100 words
            continue
        row[-1] = text
        ret.append(row)
    return ret


if __name__ == '__main__':
    print('Reading questions ...')
    with (Path(data_dir) / 'Questions.csv').open('rb') as f:
        reader = csv.reader(f)
        title = reader.next()  # Id,OwnerUserId,CreationDate,ClosedDate,Score,Title,Body
        rows = [r for r in reader]
    print('Pruning ...')
    group_size = int(0.999 + (len(rows) / cpus))
    grouped_rows = [rows[i:i+group_size] for i in range(0, len(rows), group_size)]
    p = Pool(cpus)
    ret = p.map_async(process_text, grouped_rows).get(9999999)
    p.close()
    p.join()
    rows = sum(ret, [])

    print('Writing ...')
    with (Path(out_dir) / 'PrunedQuestions.csv').open('wb') as f:
        writer = csv.writer(f)
        writer.writerows([title] + rows)
