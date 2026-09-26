from typing import TypedDict, Optional
import pandas as pd
from app.sql.generator import generate_plan, explain_error
from app.sql.executor import execute_sql
from app.pandas_tools.charts import save_chart
from app.pandas_tools.planner import generate_pandas_plan
from app.pandas_tools.executor import execute_pandas_plan
from app.pandas_tools.summarizer import generate_summary


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

    if not plan.get("steps"):
        state["result"] = None
        state["message"] = "I couldn't find relevant data to answer that question."
        return state

    df = state["dataframe"]
    result = execute_pandas_plan(df, plan)
    state["result"] = result

    if not result["success"]:
        state["message"] = explain_error(state["question"], result["error"])

    return state


def summarize_node(state: AgentState) -> AgentState:
    summary_text = generate_summary(state["question"], state["history"])
    state["message"] = summary_text
    if state["history"]:
        state["result"] = {"success": True, "data": state["history"][-1]["data"], "error": None}
    else:
        state["result"] = None
    return state


def route_after_plan(state: AgentState) -> str:
    if state["plan"].get("is_summary_request"):
        return "summarize"
    return "pandas"


def chart_node(state: AgentState) -> AgentState:
    plan = state["plan"]
    result = state["result"]
    wants_chart = plan.get("needs_chart") or plan.get("wants_chart")

    if result and result["success"] and wants_chart:
        try:
            if plan.get("is_summary_request"):
                cols = list(result["data"].columns)
                x_col, y_col = cols[0], cols[1]
                chart_type = plan.get("chart_type") or "bar"
            else:
                x_col, y_col = plan["x_col"], plan["y_col"]
                chart_type = plan["chart_type"]

            path = save_chart(
                result["data"],
                x_col=x_col,
                y_col=y_col,
                chart_type=chart_type,
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
    graph.add_node("summarize", summarize_node)
    graph.add_node("chart", chart_node)

    graph.set_entry_point("plan")
    graph.add_conditional_edges(
        "plan",
        route_after_plan,
        {"pandas": "pandas", "summarize": "summarize"}
    )
    graph.add_edge("pandas", "chart")
    graph.add_edge("summarize", "chart")
    graph.add_edge("chart", END)

    return graph.compile()