import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langsmith import traceable

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))


@traceable
def generate_pandas_plan(question: str, schema: str, history: list = None) -> dict:
    history_text = ""
    if history:
        history_text = "\n\nPrevious questions asked in this conversation:\n"
        for turn in history:
            history_text += f"Q: {turn['question']}\nOperation used: {turn.get('operation')}\n"

    prompt = f"""
You are a data analysis assistant working with a pandas DataFrame.
The DataFrame has these columns:
{schema}
{history_text}

The user asked: {question}

Decide what operation is needed to answer this.
If the question is gibberish, unrelated to this data, or too vague to determine what's being asked, set "operation" to null instead of guessing.
Respond with ONLY a JSON object, no other text, in this exact format:
{{
  "operation": "groupby" or "filter" or "value_counts" or "describe" or "raw",
  "column": "the main column to operate on, or null",
  "value_column": "the numeric column to aggregate (for groupby/describe), or null",
  "agg": "count" or "mean" or "sum" or "min" or "max" or null,
  "filter_column": "column to filter on, or null",
  "filter_value": "value to filter for, or null",
  "needs_chart": true or false,
  "chart_type": "bar" or "line" or "pie" or "scatter" or "histogram" or "box" or null,
  "x_col": "column name for x-axis, or null if no chart",
  "y_col": "column name for y-axis, or null if no chart",
  "chart_title": "a short, clean title for the chart, or null if no chart"
}}

Operation meanings:
- groupby: aggregate value_column grouped by "column" (e.g. average Profit by Region → column=Region, value_column=Profit, agg=mean)
- filter: return rows matching a condition (e.g. Segment = Consumer) — requires filter_column and filter_value
- value_counts: count occurrences of each unique value in a CATEGORICAL column (e.g. how many orders per Ship Mode) — requires "column". Do NOT use on continuous numeric columns.
- describe: summary statistics (mean, min, max, std) of a NUMERIC column, use this for questions about "distribution", "spread", "range", or "average/typical value" of a number — requires value_column
- raw: return the data as-is, no aggregation (used only when the user just wants to see/chart existing data)

Only set needs_chart to true if the user explicitly asks for a chart, graph, plot, or visualization.
The x_col and y_col values must exactly match column names in the schema above.
"""
    response = llm.invoke(prompt)
    raw = response.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)