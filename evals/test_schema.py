from app.sql.schema import get_schema
from app.sql.generator import generate_sql
from app.sql.executor import execute_sql

schema = get_schema()

question = "List all customers whose first name is 'MARY'."

sql = generate_sql(question, schema)
print("Generated SQL:\n", sql)

results = execute_sql(sql)
print("\nResults:")
for row in results:
    print(row)