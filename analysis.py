# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Utilities: Caching & Style

# %%
import pandas as pd
import os
from google.cloud import bigquery

GCP_PROJECT = "your-gcp-project-id"  # replace with your project ID

def get_data(sql, project_id=GCP_PROJECT, force=False):
    cache_path = f"cache/{pd.util.hash_pandas_object(pd.Series([sql])).iloc[0]}.parquet"
    os.makedirs("cache", exist_ok=True)

    if os.path.exists(cache_path) and not force:
        print("Loading from cache...")
        return pd.read_parquet(cache_path)

    client = bigquery.Client(project=project_id)
    df = client.query(sql).to_dataframe()
    df.to_parquet(cache_path)
    return df
