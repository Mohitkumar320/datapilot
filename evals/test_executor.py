from app.pandas_tools.loader import load_csv
from app.pandas_tools.executor import execute_pandas_plan

result = load_csv("data/samplesuperstore.csv")   # your actual filename
df = result["data"]

plan = {
    "operation": "raw",
    "column": None, "value_column": None, "agg": None,
    "filter_column": None, "filter_value": None,
    "needs_chart": False, "chart_type": None, "x_col": None, "y_col": None, "chart_title": None
}

output = execute_pandas_plan(df, plan)
print(output["success"])
print(output["data"])
print(output["error"])