#!/usr/bin/env python

import csv
from dataclasses import dataclass, asdict, fields
import json
import itertools as it
import operator as op
import re
import typing as ty

import click
import requests

BIT_SCORE_IDX = 14

@dataclass
class Info:
    structure: str
    structure_title: str
    chain_length: int
    chain_organism: str
    chain_title: str
    suggested_name: str
    model_length: int
    bit_score: float
    cutoff_score: float
    e_value: float
    suggested_accession: str


def get_summary(pdb_id: str):
    response = requests.get(f"https://www.ebi.ac.uk/pdbe/api/pdb/entry/summary/{pdb_id}")
    response.raise_for_status()
    data = response.json()
    return data[pdb_id][0]



def fetch_info(id: str):
    pdb_id, chain_id = id.split('_')
    response = requests.get(f"https://www.ebi.ac.uk/pdbe/api/pdb/entry/molecules/{pdb_id}")
    response.raise_for_status()
    data = response.json()
    summary = get_summary(pdb_id)
    for entity in data[pdb_id]:
        if chain_id in entity['in_chains']:
            return {
                'structure_title': summary['title'],
                'chain_title': ';'.join(entity['molecule_name']),
                'chain_organism': ';' .join(s['organism_scientific_name'] or '' for s in entity['source']),
                'chain_length': len(entity['sequence']),
            }
    raise ValueError(f"Did not find data for {id}")


def parse_hits(handle):
    for row in handle:
        if row.startswith('#'):
            continue
        parts = re.split(r'\s+', row, maxsplit=18)
        parts[BIT_SCORE_IDX] = float(parts[BIT_SCORE_IDX])
        parts[BIT_SCORE_IDX + 1] = float(parts[BIT_SCORE_IDX + 1])
        yield parts


def build_sheet(models, handle) -> ty.Iterator[Info]:
    grouped = it.groupby(parse_hits(handle), op.itemgetter(2))
    for (structure, hits) in grouped:
        best_hit = max(hits, key=op.itemgetter(BIT_SCORE_IDX))
        structure_info = fetch_info(structure)
        yield Info(
            structure=structure,
            structure_title=structure_info['structure_title'],
            chain_organism=structure_info['chain_organism'],
            chain_title=structure_info['chain_title'],
            chain_length=structure_info['chain_length'],
            suggested_name=best_hit[0],
            model_length=models[best_hit[1]]['clen'],
            bit_score=float(best_hit[BIT_SCORE_IDX]),
            cutoff_score=models[best_hit[1]]['bit-score'],
            e_value=float(best_hit[BIT_SCORE_IDX + 1]),
            suggested_accession=best_hit[1],
        )


@click.command()
@click.argument('hits', default='-', type=click.File('r'))
@click.argument('model-info', type=click.File('r'))
@click.argument('output', default='-', type=click.File('w'))
def main(hits, model_info, output):
    models = json.load(model_info)
    sheet = build_sheet(models, hits)
    fieldnames = [field.name for field in fields(Info)]
    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=',')
    writer.writeheader()
    writer.writerows(asdict(d) for d in sheet)


if __name__ == '__main__':
    main()
