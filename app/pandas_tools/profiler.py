import pandas as pd


def _num(x):
    # JSON can't carry NaN, so an all-empty column returns None instead
    return None if pd.isna(x) else round(float(x), 2)


def profile_dataframe(df: pd.DataFrame) -> dict:
    columns = []
    for col in df.columns:
        s = df[col]
        info = {
            "name": col,
            "type": str(s.dtype),
            "nulls": int(s.isna().sum()),
            "unique": int(s.nunique()),
        }
        if pd.api.types.is_numeric_dtype(s):
            info["min"] = _num(s.min())
            info["max"] = _num(s.max())
            info["mean"] = _num(s.mean())
            info["median"] = _num(s.median())

        modes = s.mode()
        if len(modes) > 0:
            top = modes.iloc[0]
            info["top"] = _num(top) if pd.api.types.is_numeric_dtype(s) else str(top)
            info["top_count"] = int((s == top).sum())

        columns.append(info)

    return {"rows": int(len(df)), "columns": columns}