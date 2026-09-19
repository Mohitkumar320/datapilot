from app.sql.schema import get_schema
from app.sql.generator import generate_sql
from app.sql.executor import execute_sql

def ask(question: str):
    schema = get_schema()
    sql = generate_sql(question, schema)
    print("Generated SQL:\n", sql)

    result = execute_sql(sql)
    if result["success"]:
        print("\nResults:")
        for row in result["data"]:
            print(row)
    else:
        print("\nQuery failed:", result["error"])

if __name__ == "__main__":
    question = input("Ask a question about the database: ")
    ask(question)