#!/usr/bin/env python


import csv
import collections as coll
from io import StringIO

import click
import requests

from Bio import SeqIO


def fetch_sequences(handle):
    # pdb_ids = []
    # requested = coll.defaultdict(list)
    for (pdb_id, chain_id) in csv.reader(handle, delimiter='\t'):
        # pdb_ids.append(pdb_id)
        # requested[pdb_id].append(chain_id)

        response = requests.get(f"https://www.ebi.ac.uk/pdbe/entry/pdb/{pdb_id}/fasta")
        response.raise_for_status()
        handle = StringIO(response.text)
        for record in SeqIO.parse(handle, 'fasta'):
            parts = record.description.split('|')
            chain_ids = set(parts[2].split(' '))
            if chain_id in chain_ids:
                record.id = f"{pdb_id}_{chain_id}"
                yield record


@click.command()
@click.argument('missing', default='-', type=click.File('r'))
@click.argument('output', default='-', type=click.File('w'))
def main(missing, output):
    SeqIO.write(fetch_sequences(missing), output, 'fasta')


if __name__ == '__main__':
    main()
