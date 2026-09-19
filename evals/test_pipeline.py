from app.sql.schema import get_schema
from app.sql.generator import generate_sql
from app.sql.executor import execute_sql

schema = get_schema()
question = "Find all customers who own a spaceship."

sql = generate_sql(question, schema)
print("Generated SQL:\n", sql)

result = execute_sql(sql)

if result["success"]:
    print("\nResults:")
    for row in result["data"]:
        print(row)
else:
    print("\nQuery failed:", result["error"])