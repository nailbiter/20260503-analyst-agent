import json
import os
from pathlib import Path

import click
from dotenv import load_dotenv
from google.cloud import bigquery
from tqdm import tqdm

load_dotenv()
GCP_PROJECT = os.environ.get("GCP_PROJECT")


def dump_table(client, table_ref):
    table = client.get_table(table_ref)
    meta = table.to_api_repr()
    out = Path(f".data/bigquery-metadata-dump/{table.project}/{table.dataset_id}/{table.table_id}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(meta, indent=2))


@click.command()
@click.option("-p", "--project", multiple=True, help="Dump all tables in all datasets of this project.")
@click.option("-d", "--dataset", multiple=True, help="Dump all tables in this dataset (bare name uses GCP_PROJECT; or 'project.dataset').")
@click.option("-t", "--table", multiple=True, help="Dump a specific table (fully qualified: project.dataset.table).")
def main(project, dataset, table):
    client = bigquery.Client(project=GCP_PROJECT)
    table_refs = list(table)

    for proj in project:
        for ds in client.list_datasets(proj):
            for tbl in client.list_tables(ds.reference):
                table_refs.append(tbl.reference)

    for ds_str in dataset:
        parts = ds_str.split(".")
        if len(parts) == 2:
            proj_id, ds_id = parts
        else:
            proj_id, ds_id = GCP_PROJECT, parts[0]
        ds_ref = bigquery.DatasetReference(proj_id, ds_id)
        for tbl in client.list_tables(ds_ref):
            table_refs.append(tbl.reference)

    for ref in tqdm(table_refs, desc="Dumping metadata"):
        dump_table(client, ref)


if __name__ == "__main__":
    main()
