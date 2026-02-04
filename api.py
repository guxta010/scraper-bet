from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
import json
import os

app = FastAPI()

SECRET = os.getenv("SCRAPER_SECRET", "changeme")
ARQUIVO = "palpites.json"


@app.post("/upload-palpites")
def upload_palpites(
    dados: dict,
    x_secret: str = Header(None)
):
    if x_secret != SECRET:
        return JSONResponse(
            status_code=401,
            content={"erro": "Não autorizado"}
        )

    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return {"status": "ok", "total": len(dados.get("palpites", []))}


@app.get("/palpites")
def get_palpites():
    if not os.path.exists(ARQUIVO):
        return JSONResponse(
            status_code=404,
            content={"erro": "palpites.json não encontrado"}
        )

    with open(ARQUIVO, "r", encoding="utf-8") as f:
        dados = json.load(f)

    return JSONResponse(content=dados)
