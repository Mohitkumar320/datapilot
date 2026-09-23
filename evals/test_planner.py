from app.pandas_tools.loader import load_csv, get_dataframe_schema
from app.pandas_tools.planner import generate_pandas_plan

result = load_csv("data/samplesuperstore.csv")   # your actual filename
df = result["data"]
schema = get_dataframe_schema(df)

question = "What's the distribution of Discount values?"
plan = generate_pandas_plan(question, schema)

print(plan)