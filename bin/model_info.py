#!/usr/bin/env python

import csv
import json

import click

def load_models(handle):
    reader = csv.DictReader(handle)
    return list(reader)


def load_cut(handle):
    reader = csv.DictReader(handle)
    return list(reader)


@click.command()
@click.argument('model-info', type=click.File('r'))
@click.argument('cut-ga-info', type=click.File('r'))
@click.argument('output', default='-', type=click.File('w'))
def main(model_info, cut_ga_info, output):
    models = load_models(model_info)
    cuts = load_cut(cut_ga_info)
    assert len(models) == len(cuts)
    merged = {}
    for (model, cut) in zip(models, cuts):
        assert model['idx'] == cut['idx']
        assert model['accession'] == cut['accession']
        entry = {}
        entry.update(cut)
        entry.update(model)
        merged[model['accession']] = entry

    json.dump(merged, output)


if __name__ == '__main__':
    main()
