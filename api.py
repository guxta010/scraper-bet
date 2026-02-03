from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import os

app = FastAPI()

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