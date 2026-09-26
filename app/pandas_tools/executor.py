import pandas as pd


def _run_single_operation(df: pd.DataFrame, step: dict) -> pd.DataFrame:
    operation = step.get("operation")

    if operation == "groupby":
        column = step["column"]
        value_column = step["value_column"]
        agg = step["agg"]
        return df.groupby(column)[value_column].agg(agg).reset_index()

    elif operation == "filter":
        filter_column = step["filter_column"]
        filter_value = step["filter_value"]

        if isinstance(filter_column, list) or isinstance(filter_value, list):
            raise ValueError(
                f"Filter step must have single column/value, got lists: "
                f"{filter_column} / {filter_value}. Planner should split into separate steps."
            )

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

    else:
        raise ValueError(f"Unknown operation: {operation}")

def execute_pandas_plan(df: pd.DataFrame, plan: dict) -> dict:
    try:
        steps = plan.get("steps")
        if not steps:
            return {"success": False, "data": None, "error": "No operation steps provided"}

        result = df
        for step in steps:
            result = _run_single_operation(result, step)

        return {"success": True, "data": result, "error": None}

    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}