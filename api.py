from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import os
import subprocess

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PALPITES_PATH = os.path.join(BASE_DIR, "palpites.json")

@app.get("/")
def home():
    return {"status": "ok", "service": "forebet-scraper-api"}

@app.get("/run-scraper")
def run_scraper():
    try:
        subprocess.run(
            ["python", "scraper.py"],
            cwd=BASE_DIR,
            check=True
        )
        return {"status": "ok", "message": "Scraper executado com sucesso"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"erro": str(e)}
        )

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
