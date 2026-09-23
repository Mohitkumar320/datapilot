# app/main.py

from app.sql.schema import get_schema
from app.pandas_tools.loader import load_csv, get_dataframe_schema
from app.agents.graph import build_graph, build_csv_graph


def ask(question: str, schema: str, history: list, graph, dataframe=None):
    initial_state = {
        "question": question,
        "schema": schema,
        "history": history,
        "plan": None,
        "result": None,
        "chart_path": None,
        "message": None,
        "dataframe": dataframe
    }

    final_state = graph.invoke(initial_state)

    plan = final_state["plan"]
    result = final_state["result"]

    if final_state["message"]:
        print("\n", final_state["message"])
    elif result and result["success"]:
        print("\nResults:")
        print(result["data"])
        if final_state["chart_path"]:
            print("\nChart saved to:", final_state["chart_path"])

    history.append({
        "question": question,
        "sql": plan.get("sql"),
        "operation": plan.get("operation")
    })


if __name__ == "__main__":
    mode = input("Use (1) Database or (2) CSV file? Enter 1 or 2: ").strip()

    history = []

    if mode == "2":
        file_path = input("Enter path to your CSV file: ").strip()
        load_result = load_csv(file_path)
        if not load_result["success"]:
            print("Failed to load CSV:", load_result["error"])
            exit()
        dataframe = load_result["data"]
        schema = get_dataframe_schema(dataframe)
        graph = build_csv_graph()
        
    else:
        dataframe = None
        schema = get_schema()
        graph = build_graph()

    print("Ask questions about your data. Type 'exit' to quit.\n")

    while True:
        question = input("\nYour question: ")
        if question.lower() in ("exit", "quit"):
            print("Goodbye.")
            break
        ask(question, schema, history, graph, dataframe)