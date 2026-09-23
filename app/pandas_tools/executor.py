

import pandas as pd


def execute_pandas_plan(df: pd.DataFrame, plan: dict) -> dict:
    try:
        operation = plan.get("operation")

        if operation == "groupby":
            column = plan["column"]
            value_column = plan["value_column"]
            agg = plan["agg"]
            result = df.groupby(column)[value_column].agg(agg).reset_index()

        elif operation == "filter":
            filter_column = plan["filter_column"]
            filter_value = plan["filter_value"]
            result = df[df[filter_column] == filter_value]

        elif operation == "value_counts":
            column = plan["column"]
            result = df[column].value_counts().reset_index()
            result.columns = [column, "count"]

        elif operation == "describe":
            value_column = plan["value_column"]
            result = df[value_column].describe().reset_index()
            result.columns = ["stat", "value"]

        elif operation == "raw":
            result = df

        else:
            return {"success": False, "data": None, "error": f"Unknown operation: {operation}"}

        return {"success": True, "data": result, "error": None}

    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}