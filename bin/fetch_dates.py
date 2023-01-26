#!/usr/bin/env python

import csv

import click
import requests

from Bio import SeqIO


def fetch_sequences(handle):
    for (pdb_id, chain_id) in csv.reader(handle, delimiter='\t'):
        response = requests.get(f"https://www.ebi.ac.uk/pdbe/api/pdb/entry/summary/{pdb_id}")
        response.raise_for_status()
        data = response.json()
        raw_date = data[pdb_id][0]['deposition_date']
        yield { 'structure': f"{pdb_id}_{chain_id}", 'date': raw_date }


@click.command()
@click.argument('missing', default='-', type=click.File('r'))
@click.argument('output', default='-', type=click.File('w'))
def main(missing, output):
    writer = csv.DictWriter(output, fieldnames=['structure', 'date'], delimiter=',')
    writer.writeheader()
    writer.writerows(fetch_sequences(missing))


if __name__ == '__main__':
    main()
