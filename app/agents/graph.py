from typing import TypedDict, Optional
import pandas as pd
from app.sql.generator import generate_plan, explain_error
from app.sql.executor import execute_sql
from app.pandas_tools.charts import save_chart
from app.pandas_tools.planner import generate_pandas_plan
from app.pandas_tools.executor import execute_pandas_plan


class AgentState(TypedDict):
    question: str
    schema: str
    history: list
    plan: Optional[dict]
    result: Optional[dict]
    chart_path: Optional[str]
    message: Optional[str]
    dataframe: Optional[pd.DataFrame]


def plan_node(state: AgentState) -> AgentState:
    plan = generate_plan(state["question"], state["schema"], state["history"])
    state["plan"] = plan
    return state


def sql_node(state: AgentState) -> AgentState:
    sql = state["plan"]["sql"]
    if not sql:
        state["result"] = None
        state["message"] = "I couldn't find relevant data in the database to answer that question."
        return state

    result = execute_sql(sql)
    state["result"] = result

    if not result["success"]:
        state["message"] = explain_error(state["question"], result["error"])

    return state


def plan_node_csv(state: AgentState) -> AgentState:
    plan = generate_pandas_plan(state["question"], state["schema"], state["history"])
    state["plan"] = plan
    return state


def pandas_node(state: AgentState) -> AgentState:
    plan = state["plan"]

    if not plan.get("operation"):
        state["result"] = None
        state["message"] = "I couldn't find relevant data to answer that question."
        return state

    df = state["dataframe"]
    result = execute_pandas_plan(df, plan)
    state["result"] = result

    if not result["success"]:
        state["message"] = explain_error(state["question"], result["error"])

    return state


def chart_node(state: AgentState) -> AgentState:
    plan = state["plan"]
    result = state["result"]

    if result and result["success"] and plan["needs_chart"]:
        try:
            path = save_chart(
                result["data"],
                x_col=plan["x_col"],
                y_col=plan["y_col"],
                chart_type=plan["chart_type"],
                title=plan.get("chart_title") or state["question"],
                filename="latest_chart.png"
            )
            state["chart_path"] = path
        except Exception as e:
            state["message"] = explain_error(state["question"], str(e))

    return state


from langgraph.graph import StateGraph, END

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("plan", plan_node)
    graph.add_node("sql", sql_node)
    graph.add_node("chart", chart_node)

    graph.set_entry_point("plan")
    graph.add_edge("plan", "sql")
    graph.add_edge("sql", "chart")
    graph.add_edge("chart", END)

    return graph.compile()


def build_csv_graph():
    graph = StateGraph(AgentState)

    graph.add_node("plan", plan_node_csv)
    graph.add_node("pandas", pandas_node)
    graph.add_node("chart", chart_node)

    graph.set_entry_point("plan")
    graph.add_edge("plan", "pandas")
    graph.add_edge("pandas", "chart")
    graph.add_edge("chart", END)

    return graph.compile()