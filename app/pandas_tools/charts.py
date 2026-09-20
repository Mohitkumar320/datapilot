import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

def save_chart(df, x_col: str, y_col: str = None, chart_type: str = "bar", title: str = "Chart", filename: str = "chart.png"):
    os.makedirs("outputs", exist_ok=True)
    path = os.path.join("outputs", filename)

    plt.figure(figsize=(8, 5))

    if chart_type == "bar":
        plt.bar(df[x_col], df[y_col])
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.xticks(rotation=45, ha="right")

    elif chart_type == "line":
        plt.plot(df[x_col], df[y_col], marker="o")
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.xticks(rotation=45, ha="right")

    elif chart_type == "pie":
        plt.pie(df[y_col], labels=df[x_col], autopct="%1.1f%%")

    elif chart_type == "scatter":
        plt.scatter(df[x_col], df[y_col])
        plt.xlabel(x_col)
        plt.ylabel(y_col)

    elif chart_type == "histogram":
        plt.hist(df[x_col], bins=20)
        plt.xlabel(x_col)
        plt.ylabel("Frequency")

    elif chart_type == "box":
        df.boxplot(column=y_col, by=x_col)
        plt.xlabel(x_col)
        plt.ylabel(y_col)

    else:
        raise ValueError(f"Unsupported chart_type: {chart_type}")

    plt.title(title)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path