from app.sql.schema import get_schema
from app.sql.generator import generate_plan, explain_error
from app.sql.executor import execute_sql
from app.pandas_tools.charts import save_chart

def ask(question: str, schema: str, history: list):
    plan = generate_plan(question, schema, history)
    print("DEBUG PLAN:", plan)

    sql = plan["sql"]
    print("Generated SQL:\n", sql)

    if not sql:
        print("\nI couldn't find relevant data in the database to answer that question. Could you rephrase, or ask about something the database actually tracks?")
    else:
        result = execute_sql(sql)
        if result["success"]:
            df = result["data"]
            print("\nResults:")
            print(df)

            if plan["needs_chart"]:
                try:
                    chart_path = save_chart(
                        df,
                        x_col=plan["x_col"],
                        y_col=plan["y_col"],
                        chart_type=plan["chart_type"],
                        title=plan.get("chart_title") or question,
                        filename="latest_chart.png"
                    )
                    print("\nChart saved to:", chart_path)
                except Exception as chart_err:
                    friendly = explain_error(question, str(chart_err))
                    print("\n", friendly)
        else:
            friendly = explain_error(question, result["error"])
            print("\n", friendly)

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