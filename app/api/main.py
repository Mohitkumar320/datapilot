import shutil
import os

import pandas as pd

from app.pandas_tools.profiler import profile_dataframe
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.pandas_tools.loader import load_csv, get_dataframe_schema
from app.agents.graph import build_csv_graph, build_graph
from app.sql.schema import get_schema
from app.main import ask as run_ask

app = FastAPI()

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="frontend"), name="static")

sessions: dict[str, dict] = {}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class AskRequest(BaseModel):
    session_id: str
    question: str


class DBConnectRequest(BaseModel):
    session_id: str
    host: str
    port: int = 3306
    user: str
    password: str
    database: str


@app.get("/health")
def health():
    return {"status": "ok"}


from fastapi import Form

@app.post("/upload-csv")
def upload_csv(session_id: str = Form(...), file: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_DIR, f"{session_id}.csv")

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    load_result = load_csv(save_path)
    if not load_result["success"]:
        return {"error": load_result["error"]}

    dataframe = load_result["data"]
    schema = get_dataframe_schema(dataframe)
    graph = build_csv_graph()

    sessions[session_id] = {
        "dataframe": dataframe,
        "db_config": None,
        "schema": schema,
        "graph": graph,
        "history": []
    }

    return {
        "session_id": session_id,
        "message": "CSV loaded",
        "rows": len(dataframe),
        "profile": profile_dataframe(dataframe),
    }

@app.post("/connect-db")
def connect_db(req: DBConnectRequest):
    db_config = {
        "host": req.host,
        "port": req.port,
        "user": req.user,
        "password": req.password,
        "database": req.database
    }

    try:
        schema = get_schema(db_config)
    except Exception as e:
        return {"error": f"Could not connect to database: {str(e)}"}

    graph = build_graph()

    sessions[req.session_id] = {
        "dataframe": None,
        "db_config": db_config,
        "schema": schema,
        "graph": graph,
        "history": []
    }

    return {"session_id": req.session_id, "message": "Connected to database"}


@app.post("/ask")
def ask_endpoint(req: AskRequest):
    if req.session_id not in sessions:
        return {"error": "Session not found. Upload a CSV or connect a database first."}

    session = sessions[req.session_id]

    run_ask(
        req.question,
        session["schema"],
        session["history"],
        session["graph"],
        session["dataframe"],
        session.get("db_config")
    )

    last = session["history"][-1]

    data = last["data"]
    if isinstance(data, pd.DataFrame):
        data_records = data.to_dict(orient="records")
    else:
        data_records = data
    return {
        "session_id": req.session_id,
        "question": last["question"],
        "steps": last["steps"],
        "data": data_records,
        "chart_path": last["chart_path"],
        "message": last["message"],
    }


@app.get("/chart")
def get_chart():
    chart_path = "outputs/latest_chart.png"
    if not os.path.exists(chart_path):
        return {"error": "No chart available yet."}
    return FileResponse(
        chart_path,
        media_type="image/png",
        headers={"Cache-Control": "no-store"}
    )