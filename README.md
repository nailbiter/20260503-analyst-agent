Since you have "god access" at home and a personal Claude Code subscription, we can build the ultimate "Warm-Kernel" lab. [cite_start]We will use the **theLook eCommerce** public dataset in BigQuery, which is perfect for supply chain scenarios (orders, inventory, products). [cite: 71, 76]

Here is your step-by-step guide to setting up the **Jupyter MCP + Jupytext** workflow.

### Phase 1: The BigQuery Sandbox
1.  **Google Cloud Project**: Ensure you have a GCP project with the **BigQuery API** enabled.
2.  **Authentication**: Run `gcloud auth application-default login` in your terminal so your local Python environment can reach BigQuery without hardcoded keys.
3.  **The Dataset**: We will use `bigquery-public-data.thelook_ecommerce`. [cite_start]It has tables like `orders`, `order_items`, and `inventory_items` that mirror your work at MegaThread Retail (alias). [cite: 3]

---

### Phase 2: Environment & Jupytext Setup
[cite_start]Install the core toolkit to manage the "Script-Notebook" bridge: [cite: 101, 108]

```bash
# Core data stack
uv add pandas pandas-gbq pyarrow google-cloud-bigquery jupyterlab jupytext
```

The JupyterLab extension is bundled with the `jupytext` package and activates automatically on server start — no separate extension install needed.

To enable `.ipynb` ↔ `.py` pairing for all notebooks in the project, add this to `pyproject.toml`:

```toml
[tool.jupytext]
formats = "ipynb,py:percent"
```

Or pair a single notebook once via CLI:

```bash
jupytext --set-formats ipynb,py:percent analysis.py
```

**Why this matters**: Claude Code will edit the `.py` file (clean text), while you keep the `.ipynb` open in Jupyter Lab to see the results. Jupytext keeps them in perfect sync.

---

### Phase 3: The "Warm-Kernel" (Jupyter MCP)
[cite_start]This is the "secondary objective" you asked for: giving Claude tools to "look" at data and execute code in a live session. [cite: 19, 20]

1.  **No install needed**: The MCP server (`mcp-jupyter` by Block) runs via `uvx` which is already available with uv.

2.  **Configure Claude Code**: Create `.mcp.json` at the project root:
    ```json
    {
      "mcpServers": {
        "jupyter": {
          "command": "uvx",
          "args": ["mcp-jupyter"],
          "env": { "TOKEN": "YOUR_JUPYTER_TOKEN" }
        }
      }
    }
    ```

3.  **Start JupyterLab with a matching token**:
    ```bash
    jupyter lab --IdentityProvider.token YOUR_JUPYTER_TOKEN
    ```

4.  **The Result**: When you run Claude Code in your project folder, it will have tools like `execute_code` and `list_variables` to see your dataframe in real-time.

---

### Phase 4: Defining the Agent Logic
Create a folder named `.claude/agents/` in your project and add a file called `supply_chain_analyst.md`. [cite_start]This encodes your interaction style. [cite: 40, 88, 89]

```markdown
# Role: Junior Analyst Super-Charger
You are an expert Data Analyst. Your goal is to minimize my "copy-paste" tax.

## Operating Rules
1. [cite_start]**Caching First**: Use the `get_data` helper to cache BigQuery results as `.parquet`. [cite: 66, 95]
2. **Dual-Artifacts**: Every request for "data" must result in:
   - [cite_start]A Matplotlib/Seaborn visualization. [cite: 64, 96]
   - [cite_start]A `styled_table.xlsx` using Pandas Styler (highlighting outliers). [cite: 54, 64]
3. **Smart Inspection**: 
   - For small data, show me the head. 
   - [cite_start]For large data, run `df.corr()` or `df.describe()` via MCP instead of printing the whole frame. [cite: 73]
4. [cite_start]**Notebook Integrity**: Only edit the `.py` version of the paired notebook. [cite: 60, 106]
```

---

### Phase 5: The "Golden Cell"
[cite_start]Start your notebook with this "utility cell" to handle the state-management you mentioned. [cite: 90, 91]

```python
# %% [markdown]
# ## Utilities: Caching & Style
# %%
import pandas as pd
import os
from google.cloud import bigquery

def get_data(sql, project_id, force=False):
    cache_path = f"cache/{pd.util.hash_pandas_object(pd.Series([sql])).iloc[0]}.parquet"
    os.makedirs("cache", exist_ok=True)
    
    if os.path.exists(cache_path) and not force:
        print("Loading from cache...")
        return pd.read_parquet(cache_path)
    
    client = bigquery.Client(project=project_id)
    df = client.query(sql).to_dataframe()
    df.to_parquet(cache_path)
    return df
```

---

### Testing the Workflow
1.  **Launch Jupyter Lab**: Open `analysis.ipynb`.
2.  **Launch Claude Code**: In your terminal, run `claude`.
3.  [cite_start]**The Command**: "Claude, using the `supply_chain_analyst` agent, analyze the `thelook_ecommerce` data. Find the monthly stockout trend for the 'Swimwear' category. Cache the data and give me the two sets of artifacts." [cite: 92]

**What happens next**: Claude will write the SQL, use MCP to run the cell and test it, save the parquet file, and generate your chart and Excel file. [cite_start]You just sit back and watch the notebook update itself. [cite: 93, 94, 95, 96]

How does this setup look to you for a first home trial?
