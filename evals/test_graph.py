from app.sql.schema import get_schema
from app.agents.graph import build_graph

schema = get_schema()
graph = build_graph()

initial_state = {
    "question": "Show total rentals per category as a bar chart.",
    "schema": schema,
    "history": [],
    "plan": None,
    "result": None,
    "chart_path": None,
    "message": None
}

final_state = graph.invoke(initial_state)
print(final_state)