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
            history_text += f"Q: {turn['question']}\nSteps used: {turn.get('steps')}\n"

    prompt = f"""
You are a data analysis assistant working with a pandas DataFrame.
The DataFrame has these columns:
{schema}
{history_text}

The user asked: {question}

Decide what sequence of operations is needed to answer this. Most questions need only ONE step.
Some questions need TWO steps chained together — most commonly a filter followed by an aggregation
(e.g. "average Profit by Sub-Category for Consumer segment" = filter Segment=Consumer, THEN groupby Sub-Category on Profit).

If the question is gibberish, unrelated to this data, or too vague to determine what's being asked, return an empty steps list instead of guessing.

Respond with ONLY a JSON object, no other text, in this exact format:
{{
  "steps": [
    {{
      "operation": "groupby" or "filter" or "value_counts" or "describe" or "raw" or "profile" or "correlation" or "outlier",
      "column": "the main column to operate on, or null",
      "value_column": "the numeric column to aggregate (for groupby/describe), or null",
      "agg": "count" or "mean" or "sum" or "min" or "max" or null,
      "filter_column": "a SINGLE column name to filter on (string, never a list), or null",
      "filter_value": "a SINGLE value to filter for (string/number, never a list), or null",
      "filter_value": "a value to filter for. Normally a SINGLE string/number. For 'is one of several values' questions (e.g. Consumer OR Corporate), use a LIST of values instead, or null",
      "sort_order": "asc" or "desc" or null,
      "limit": "a number, or null",
      "limit": "a number, or null",
      "post_op": "percent_of_total" or "ratio" or "rank" or null,
      "ratio_column": "a second numeric column to divide value_column by, only used when post_op is 'ratio', or null"
    }}
  ],
  "needs_chart": true or false,
  "chart_type": "bar" or "line" or "pie" or "scatter" or "histogram" or "box" or null,
  "x_col": "column name for x-axis, or null if no chart",
  "y_col": "column name for y-axis, or null if no chart",
  "chart_title": "a short, clean title for the chart, or null if no chart",
  "is_summary_request": true or false,
  "wants_chart": true or false
}}

Operation meanings:
- groupby: aggregate value_column grouped by "column" (e.g. average Profit by Region → column=Region, value_column=Profit, agg=mean)
- filter: return rows matching a condition (e.g. Segment = Consumer) — requires filter_column and filter_value, each a SINGLE scalar value. When chained before another step, later steps operate on the FILTERED data.
- value_counts: count occurrences of each unique value in a CATEGORICAL column (e.g. how many orders per Ship Mode) — requires "column". Do NOT use on continuous numeric columns.
- describe: summary statistics (mean, min, max, std) of a NUMERIC column, use this for questions about "distribution", "spread", "range", or "average/typical value" of a number — requires value_column
- raw: return the data as-is, no aggregation (used only when the user just wants to see/chart existing data)
- profile: questions about the dataset ITSELF, not about values inside it: column names, how many rows or columns, data types, null/missing values, unique counts, or a general "describe/overview of the data" request. Use exactly ONE step with operation "profile" and every other field null. This is different from "describe" (statistics of one numeric column) and different from a conversation summary request.
- correlation: measures how strongly two numeric columns move together (-1 to 1). Use for "correlation between X and Y", "how does X relate to Y", "how does X affect Y". Requires value_column (first numeric column) and ratio_column (second numeric column). If the question asks for this broken down by a category (e.g. "by Region"), also set "column" to that category. Use exactly ONE step with operation "correlation".
- outlier: finds unusually high or low values in one numeric column, using a standard statistical rule. Use for "outliers", "unusual values", "anomalies" in a column. Requires value_column. Optionally set "column" to a row-identifying column (e.g. City, Order ID) so the outlier rows are recognizable. Use exactly ONE step with operation "outlier".
- post_op (attach to the LAST step only, alongside its normal fields): after that step's result is computed, apply one more calculation.
- "percent_of_total": convert value_column into each row's percentage share of the column's own total. Use for "what % of total X is Y" questions.
- "ratio": divide value_column by "ratio_column", row-wise. Use for "ratio of X to Y" or "how does X compare to Y" questions. When the question asks for the "worst" or "highest" ratio and a HIGH ratio is undesirable (e.g. "worst discount-to-profit ratio" — high discount relative to profit is bad), treat "worst" as the LOWEST value, not the highest, and set sort_order accordingly. When unsure which direction "worst" means for the specific columns involved, prefer sort_order "asc" (lowest first).
- "rank": add a rank number (1 = highest) based on value_column. Use for "rank the X by Y" questions.
Leave post_op null for ordinary questions that just need a value or a sorted/limited list.

Rules for chaining:
- If the question needs only one operation, "steps" should contain exactly ONE step object.
- If the question needs a filter applied before an aggregation, put the filter step FIRST, then the aggregation step.
- If the question needs MULTIPLE filter conditions (e.g. Segment=Consumer AND Region=West), create a SEPARATE filter step for EACH condition, chained one after another — never combine multiple columns/values into a single step using lists.
- If the question asks for the "top N", "bottom N", "highest N", "lowest N", or similar (e.g. "top 10 cities by Sales"), add "sort_order" and "limit" to the LAST step in the plan (the one whose result should be sorted and cut down). Use "desc" for "top"/"highest"/"most", "asc" for "bottom"/"lowest"/"least". Do not add a separate step for sorting.
  Example: "Average Sales for Consumer segment in the West region, grouped by Category" →
  steps = [
    {{"operation": "filter", "filter_column": "Segment", "filter_value": "Consumer"}},
    {{"operation": "filter", "filter_column": "Region", "filter_value": "West"}},
    {{"operation": "groupby", "column": "Category", "value_column": "Sales", "agg": "mean"}}
  ]
- Do not chain more than 3 steps unless the question clearly requires it.
- The chart fields (needs_chart, chart_type, x_col, y_col, chart_title) describe the chart for the FINAL result only, not intermediate steps.

Rules for summary requests:
- If the user is asking you to summarize, recap, or review everything discussed/found so far in this conversation (not asking a new data question), set "is_summary_request" to true and "steps" to an empty list — do not attempt to plan operations for a summary request.
- Set "wants_chart" to true only if the user also explicitly asks for a chart/graph/visualization of the summary.
- For all normal data questions (not summary requests), "is_summary_request" must be false.

Only set needs_chart to true if the user explicitly asks for a chart, graph, plot, or visualization.
The x_col and y_col values must exactly match column names in the schema above, or column names produced by the final step (e.g. a groupby's group-by column or aggregated value column).
"""
    response = llm.invoke(prompt)
    raw = response.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


if __name__ == "__main__":
    plan = generate_pandas_plan(
        "can you summarize everything we found so far and show a chart?",
        "Segment, Region, Sales, Profit, Sub-Category",
        history=[{"question": "average Profit by Sub-Category", "steps": []}]
    )
    print(plan)