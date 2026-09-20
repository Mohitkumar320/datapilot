import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_sql(question: str, schema: str, history: list = None) -> str:
    history_text = ""
    if history:
        history_text = "\n\nPrevious questions and answers in this conversation:\n"
        for turn in history:
            history_text += f"Q: {turn['question']}\nSQL used: {turn['sql']}\n"

    prompt = f"""
You are a SQL expert. Given this database schema:
{schema}
{history_text}

This MySQL server runs in ONLY_FULL_GROUP_BY mode: every column in the SELECT list must either appear in the GROUP BY clause or be wrapped in an aggregate function (COUNT, SUM, AVG, MAX, etc).
Write a MySQL query to answer this new question:
{question}

If the question refers to a previous result (e.g. "those", "that", "the ones"),
use the previous SQL/context to understand what it refers to.

Return ONLY the SQL query, nothing else. No explanation, no markdown formatting.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    sql = response.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def generate_plan(question: str, schema: str, history: list = None) -> dict:
    history_text = ""
    if history:
        history_text = "\n\nPrevious questions and answers in this conversation:\n"
        for turn in history:
            history_text += f"Q: {turn['question']}\nSQL used: {turn['sql']}\n"

    prompt = f"""
You are a data analysis assistant. Given this database schema:
{schema}
{history_text}

The user asked: {question}
This MySQL server runs in ONLY_FULL_GROUP_BY mode: every column in the SELECT list must either appear in the GROUP BY clause or be wrapped in an aggregate function (COUNT, SUM, AVG, MAX, etc).
Decide what is needed to answer this. Respond with ONLY a JSON object, no other text, in this exact format:
{{
  "sql": "the MySQL query to answer this",
  "needs_chart": true or false,
  "chart_type": "bar" or "line" or "pie" or "scatter" or "histogram" or "box" or null,
    "x_col": "column name to use for x-axis, or the main category/label column, or null if no chart",
  "y_col": "column name to use for y-axis, or the main value/numeric column, or null if no chart",
  "chart_title": "a short, clean title for the chart (a few words), or null if no chart"
}}

Only set needs_chart to true if the user explicitly asks for a chart, graph, plot, or visualization.
Choose chart_type based on what best fits the question: bar = comparing categories, line = trend over time, pie = proportions, scatter = relationship between two numeric variables, histogram = distribution of one numeric variable, box = spread/outliers across categories.

The x_col and y_col values must exactly match column names/aliases used in your SQL query. Pick the most meaningful columns for the chart, not necessarily the first two.

IMPORTANT: for histogram, scatter, and box chart types, the SQL must return raw individual rows (e.g. one row per film with its length), NOT pre-aggregated/grouped counts — the chart itself needs to compute the distribution from raw values.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def explain_error(question: str, error_message: str) -> str:
    prompt = f"""
The user asked this question: {question}

Behind the scenes, this technical error occurred: {error_message}

Explain in one or two simple, plain-language sentences what went wrong,
without technical jargon or error codes. Then suggest one concrete thing
the user could try instead. Do not mention SQL, MySQL, matplotlib, or any
internal implementation details.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()