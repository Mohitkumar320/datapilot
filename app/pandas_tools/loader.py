# app/pandas_tools/loader.py

import pandas as pd


def load_csv(file_path: str) -> dict:
    """
    Loads a CSV file into a pandas DataFrame.
    Returns a dict shaped like execute_sql()'s output:
    {"success": bool, "data": pd.DataFrame | None, "error": str | None}
    """
    try:
        df = pd.read_csv(file_path)

        if df.empty:
            return {
                "success": False,
                "data": None,
                "error": "The CSV file was read but contains no data."
            }

        return {
            "success": True,
            "data": df,
            "error": None
        }

    except FileNotFoundError:
        return {"success": False, "data": None, "error": f"File not found: {file_path}"}

    except pd.errors.EmptyDataError:
        return {"success": False, "data": None, "error": "The CSV file is empty."}

    except pd.errors.ParserError as e:
        return {"success": False, "data": None, "error": f"Could not parse CSV: {e}"}

    except UnicodeDecodeError:
        return {"success": False, "data": None, "error": "File encoding not supported (try saving as UTF-8)."}

    except Exception as e:
        return {"success": False, "data": None, "error": f"Unexpected error reading CSV: {e}"}


def get_dataframe_schema(df: pd.DataFrame) -> str:
    """
    Returns a plain-text description of columns and their dtypes,
    for the LLM to understand what it's working with.
    """
    lines = []
    for col in df.columns:
        lines.append(f"- {col} ({df[col].dtype})")
    return "\n".join(lines)