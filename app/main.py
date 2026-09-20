from app.sql.schema import get_schema
from app.sql.generator import generate_sql
from app.sql.executor import execute_sql

def ask(question: str, schema: str, history: list):
    sql = generate_sql(question, schema, history)
    print("Generated SQL:\n", sql)

    result = execute_sql(sql)
    if result["success"]:
        print("\nResults:")
        print(result["data"])
    else:
        print("\nQuery failed:", result["error"])

    history.append({
        "question": question,
        "sql": sql
    })

if __name__ == "__main__":
    schema = get_schema()
    history = []
    print("Ask questions about the database. Type 'exit' to quit.\n")

    while True:
        question = input("\nYour question: ")
        if question.lower() in ("exit", "quit"):
            print("Goodbye.")
            break
        ask(question, schema, history)