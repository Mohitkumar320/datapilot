import pandas as pd
from app.pandas_tools.profiler import profile_dataframe

def _run_single_operation(df: pd.DataFrame, step: dict) -> pd.DataFrame:
    operation = step.get("operation")

    if operation == "groupby":
        column = step["column"]
        value_column = step["value_column"]
        agg = step["agg"]
        ratio_column = step.get("ratio_column")

        if ratio_column:
            grouped = df.groupby(column)[[value_column, ratio_column]].agg(agg).reset_index()
        else:
            grouped = df.groupby(column)[value_column].agg(agg).reset_index()
        return grouped
    elif operation == "filter":
        filter_column = step["filter_column"]
        filter_value = step["filter_value"]

        if isinstance(filter_column, list):
            raise ValueError(
                f"Filter step must have a single column, got a list: {filter_column}. "
                f"Planner should split into separate steps."
            )

        if isinstance(filter_value, list):
            return df[df[filter_column].isin(filter_value)]

        return df[df[filter_column] == filter_value]
    
    elif operation == "value_counts":
        column = step["column"]
        result = df[column].value_counts().reset_index()
        result.columns = [column, "count"]
        return result

    elif operation == "describe":
        value_column = step["value_column"]
        result = df[value_column].describe().reset_index()
        result.columns = ["stat", "value"]
        return result

    elif operation == "raw":
        return df

    elif operation == "correlation":
        value_column = step["value_column"]
        ratio_column = step["ratio_column"]
        group_column = step.get("column")

        if group_column:
            result = (
                df.groupby(group_column)[[value_column, ratio_column]]
                .corr()
                .iloc[0::2, -1]
                .reset_index()
            )
            result.columns = [group_column, "_drop", "correlation"]
            result = result[[group_column, "correlation"]]
            result["correlation"] = result["correlation"].round(4)
            return result
        else:
            corr_value = df[value_column].corr(df[ratio_column])
            return pd.DataFrame({"correlation": [round(corr_value, 4)]})

    elif operation == "outlier":
        value_column = step["value_column"]
        id_column = step.get("column")

        q1 = df[value_column].quantile(0.25)
        q3 = df[value_column].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 3 * iqr
        upper = q3 + 3 * iqr
        mask = (df[value_column] < lower) | (df[value_column] > upper)
        cols = [id_column, value_column] if id_column else [value_column]
        return df.loc[mask, cols].reset_index(drop=True)
    else:
        raise ValueError(f"Unknown operation: {operation}")

def execute_pandas_plan(df: pd.DataFrame, plan: dict) -> dict:
    try:
        steps = plan.get("steps")
        if not steps:
            return {"success": False, "data": None, "error": "No operation steps provided"}
        
        if len(steps) == 1 and steps[0].get("operation") == "profile":
            return {"success": True, "data": profile_dataframe(df), "error": None}
        
        result = df
        for step in steps:
            result = _run_single_operation(result, step)

            post_op = step.get("post_op")
            if post_op == "percent_of_total":
                value_col = step.get("value_column") or "count"
                result[value_col] = (result[value_col] / result[value_col].sum() * 100).round(2)
            elif post_op == "ratio":
                value_col = step.get("value_column")
                ratio_col = step.get("ratio_column")
                result["ratio"] = (result[value_col] / result[ratio_col]).round(4)
            elif post_op == "rank":
                value_col = step.get("value_column") or "count"
                result["rank"] = result[value_col].rank(ascending=False, method="min").astype(int)

            sort_order = step.get("sort_order")
            limit = step.get("limit")
            if sort_order:
                sort_col = "ratio" if post_op == "ratio" else (step.get("value_column") or "count")
                result = result.sort_values(by=sort_col, ascending=(sort_order == "asc"))
            if limit:
                result = result.head(int(limit))
        return {"success": True, "data": result, "error": None}

    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}