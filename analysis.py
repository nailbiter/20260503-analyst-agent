# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
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
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()
GCP_PROJECT = os.environ["GCP_PROJECT"]

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


# %% [markdown]
# ## Swimwear Monthly Stockout Trend

# %%
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

SQL_SWIMWEAR_STOCKOUT = """
SELECT
  FORMAT_DATE('%Y-%m', DATE(created_at)) AS month,
  COUNT(*)                                                    AS total_inventory,
  COUNTIF(sold_at IS NOT NULL)                                AS items_sold,
  SAFE_DIVIDE(COUNTIF(sold_at IS NOT NULL), COUNT(*))         AS stockout_rate
FROM `bigquery-public-data.thelook_ecommerce.inventory_items`
WHERE product_category = 'Swim'
GROUP BY month
ORDER BY month
"""

df = get_data(SQL_SWIMWEAR_STOCKOUT)
df["month_dt"] = pd.to_datetime(df["month"])
print(df.head())

# %% [markdown]
# ### Artifact 1 — Visualization

# %%
fig, ax1 = plt.subplots(figsize=(14, 5))

sns.lineplot(data=df, x="month_dt", y="stockout_rate", ax=ax1,
             color="#e74c3c", linewidth=2.5, label="Stockout Rate")
ax1.set_ylabel("Stockout Rate (sold / available)", color="#e74c3c")
ax1.tick_params(axis="y", labelcolor="#e74c3c")
ax1.set_ylim(0, 1)

ax2 = ax1.twinx()
ax2.bar(df["month_dt"], df["total_inventory"], width=20,
        alpha=0.25, color="#3498db", label="Total Inventory")
ax2.set_ylabel("Total Inventory Units", color="#3498db")
ax2.tick_params(axis="y", labelcolor="#3498db")

ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
fig.autofmt_xdate(rotation=45)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.title("Swimwear — Monthly Stockout Rate vs Inventory Levels", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("swimwear_stockout_trend.png", dpi=150)
plt.close()
print("Saved: swimwear_stockout_trend.png")

# %% [markdown]
# ### Artifact 2 — Styled Excel

# %%
# Flag months where stockout_rate is above the 75th percentile (high-risk months)
threshold = df["stockout_rate"].quantile(0.75)

def highlight_outliers(row):
    color = "background-color: #f1948a" if row["Stockout Rate"] >= threshold else ""
    return [color] * len(row)

styled = (
    df[["month", "total_inventory", "items_sold", "stockout_rate"]]
    .rename(columns={
        "month":           "Month",
        "total_inventory": "Total Inventory",
        "items_sold":      "Items Sold",
        "stockout_rate":   "Stockout Rate",
    })
    .style
    .apply(highlight_outliers, axis=1)
    .format({"Stockout Rate": "{:.1%}", "Total Inventory": "{:,}", "Items Sold": "{:,}"})
    .set_caption("Swimwear Monthly Stockout Trend — rows in red exceed 75th-percentile stockout rate")
)

styled.to_excel("styled_table.xlsx", engine="openpyxl", index=False)
print("Saved: styled_table.xlsx")
