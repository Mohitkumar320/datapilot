from app.sql.schema import get_schema
from app.agents.graph import build_graph

def ask(question: str, schema: str, history: list, graph):
    initial_state = {
        "question": question,
        "schema": schema,
        "history": history,
        "plan": None,
        "result": None,
        "chart_path": None,
        "message": None
    }

    final_state = graph.invoke(initial_state)

    plan = final_state["plan"]
    result = final_state["result"]

    print("Generated SQL:\n", plan["sql"])

    if final_state["message"]:
        print("\n", final_state["message"])
    elif result and result["success"]:
        print("\nResults:")
        print(result["data"])
        if final_state["chart_path"]:
            print("\nChart saved to:", final_state["chart_path"])

    history.append({
        "question": question,
        "sql": plan["sql"]
    })

if __name__ == "__main__":
    schema = get_schema()
    history = []
    graph = build_graph()
    print("Ask questions about the database. Type 'exit' to quit.\n")

    while True:
        question = input("\nYour question: ")
        if question.lower() in ("exit", "quit"):
            print("Goodbye.")
            break
        ask(question, schema, history, graph)