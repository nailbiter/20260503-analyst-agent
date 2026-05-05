# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

**GCP auth** (required before any BigQuery queries):
```bash
gcloud auth application-default login
```

**Start JupyterLab** (required for MCP Jupyter tools):
```bash
source .envrc && jupyter lab --IdentityProvider.token $JUPYTER_TOKEN
```

**Install dependencies**:
```bash
uv sync
```

## Architecture

This is a "Warm-Kernel" analyst lab: Claude Code edits `.py` source files, Jupytext syncs them to `.ipynb`, and the Jupyter MCP server (`mcp-jupyter`) lets Claude execute code and inspect live variables in a running kernel.

- **`analysis.py` / `analysis.ipynb`**: Paired via Jupytext (`py:percent` format). **Always edit only the `.py` file** — Jupytext propagates changes to the notebook automatically.
- **`get_data(sql, force=False)`**: Core utility in `analysis.py`. Hashes the SQL string to a filename, caches results in `cache/` as Parquet, and skips BigQuery on subsequent calls unless `force=True`.
- **`.claude/agents/supply_chain_analyst.md`**: Sub-agent definition with operating rules (caching, dual-artifact output, MCP-based inspection).
- **`.mcp.json`**: Wires `mcp-jupyter` via `uvx`, connecting to the running JupyterLab using `JUPYTER_TOKEN` from `.envrc`.

## Dataset

Primary dataset: `bigquery-public-data.thelook_ecommerce` — tables include `orders`, `order_items`, `inventory_items`, `products`, `users`.
`GCP_PROJECT` is set in `.env` and loaded via `python-dotenv`.

## Agent Rules (supply_chain_analyst)

When acting as the supply chain analyst sub-agent:
1. Use `get_data` for all BigQuery queries (caching first).
2. Every data request must produce two artifacts: a Matplotlib/Seaborn chart **and** a `styled_table.xlsx` (Pandas Styler with outlier highlighting).
3. For small DataFrames show `.head()`; for large ones use MCP to run `df.describe()` or `df.corr()` in the live kernel instead of printing.
4. Only edit `analysis.py`, never `analysis.ipynb` directly.
