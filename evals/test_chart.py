from app.sql.schema import get_schema
from app.sql.generator import generate_sql
from app.sql.executor import execute_sql
from app.pandas_tools.charts import save_bar_chart

schema = get_schema()
question = "Show total rentals per film category."

sql = generate_sql(question, schema)
print("Generated SQL:\n", sql)

result = execute_sql(sql)

if result["success"]:
    df = result["data"]
    print(df)

    path = save_bar_chart(df, x_col=df.columns[0], y_col=df.columns[1], title="Rentals per Category", filename="rentals_by_category.png")
    print("\nChart saved to:", path)
else:
    print("Query failed:", result["error"])