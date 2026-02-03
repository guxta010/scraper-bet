from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import os
import subprocess

app = FastAPI()

# =============================
# Endpoint para consumir no app (Lovable)
# =============================
@app.get("/palpites")
def get_palpites():
    caminho = "palpites.json"

    if not os.path.exists(caminho):
        return JSONResponse(
            status_code=404,
            content={"erro": "palpites.json não encontrado"}
        )

    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    return JSONResponse(content=dados)


# =============================
# Endpoint para o CRON rodar o scraper
# =============================
@app.get("/run-scraper")
def run_scraper():
    try:
        subprocess.run(
            ["python", "scraper.py"],
            check=True
        )
        return {
            "status": "ok",
            "message": "Scraper executado com sucesso"
        }
    except subprocess.CalledProcessError as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "erro",
                "message": "Erro ao executar o scraper",
                "detail": str(e)
            }
        )
