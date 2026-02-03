from fastapi import FastAPI
from fastapi.responses import JSONResponse
import subprocess
import json
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PALPITES_PATH = os.path.join(BASE_DIR, "palpites.json")

@app.get("/")
def root():
    return {"status": "API online"}

@app.get("/palpites")
def get_palpites():
    if not os.path.exists(PALPITES_PATH):
        return JSONResponse(
            status_code=404,
            content={"erro": "palpites.json não encontrado"}
        )

    with open(PALPITES_PATH, "r", encoding="utf-8") as f:
        dados = json.load(f)

    return JSONResponse(content=dados)

@app.get("/run-scraper")
def run_scraper():
    try:
        subprocess.run(
            ["python", "scraper.py"],
            check=True
        )
        return {"status": "scraper executado com sucesso"}
    except subprocess.CalledProcessError as e:
        return JSONResponse(
            status_code=500,
            content={"erro": str(e)}
        )
