from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter
import time
import json

# ================= CONFIG =================

LIGAS = [
    "https://www.forebet.com/en/football-tips-and-predictions-for-brazil/serie-a",
    "https://www.forebet.com/en/football-tips-and-predictions-for-brazil/serie-b",
    "https://www.forebet.com/en/predictions-europe/uefa-champions-league",
    "https://www.forebet.com/en/predictions-europe/uefa-europa-league",
    "https://www.forebet.com/en/predictions-europe/uefa-europa-conference-league",
    "https://www.forebet.com/en/football-tips-and-predictions-for-england/premier-league",
    "https://www.forebet.com/en/football-tips-and-predictions-for-england/championship",
    "https://www.forebet.com/en/football-tips-and-predictions-for-spain/primera-division",
    "https://www.forebet.com/en/football-tips-and-predictions-for-spain/segunda-division",
    "https://www.forebet.com/en/football-tips-and-predictions-for-germany/bundesliga",
    "https://www.forebet.com/en/football-tips-and-predictions-for-germany/2-bundesliga",
    "https://www.forebet.com/en/football-tips-and-predictions-for-italy/serie-a",
    "https://www.forebet.com/en/football-tips-and-predictions-for-france/ligue1",
    "https://www.forebet.com/en/football-tips-and-predictions-for-netherlands/eredivisie",
    "https://www.forebet.com/en/football-tips-and-predictions-for-portugal/liga-portugal",
    "https://www.forebet.com/en/south-america/copa-libertadores",
    "https://www.forebet.com/en/south-america/copa-sudamericana",
    "https://www.forebet.com/en/predictions-world/world-cup"
]

HOJE = datetime.now().strftime("%Y-%m-%d")

# ================= SELENIUM =================

options = Options()

# obrigatório para rodar em nuvem (Render)
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# mantém comportamento anti-deteção (igual ao seu)
options.add_argument("--disable-blink-features=AutomationControlled")

# substitui o start-maximized (que NÃO funciona em headless)
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# ================= FUNÇÕES =================

def pegar_links_jogos(liga_url):
    driver.get(liga_url)
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = []

    for row in soup.select("div.rcnt"):
        time_tag = row.select_one("time")
        if not time_tag:
            continue

        if HOJE not in time_tag.get("datetime", ""):
            continue

        a = row.select_one("a.tnmscn")
        if not a:
            continue

        href = a.get("href", "")
        if href.startswith("/"):
            links.append("https://www.forebet.com" + href)

    return links


def analisar_jogo(url):
    driver.get(url)
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    titulo = soup.select_one("meta[itemprop='name']")
    if not titulo:
        return None

    jogo = titulo.get("content", "").strip()

    bloqueios = ["Studio", "Featured", "Live Studio", "Forebet"]
    if any(b in jogo for b in bloqueios):
        return None

    mercados = []

    # ===== FUNÇÃO INTERNA CORRETA =====
    def extrair_mercado(id_div, nome_mercado):
        tabela = soup.select_one(f"#{id_div}")
        if not tabela:
            return

        row = tabela.select_one("div.rcnt")
        if not row:
            return

        prob_span = row.select_one("div.fprc span.fpr")
        if not prob_span:
            return

        prob = int(prob_span.get_text(strip=True))

        pred_span = row.select_one("div.predict span.forepr span")
        if not pred_span:
            return

        selecao = pred_span.get_text(strip=True)

        if nome_mercado == "Vitória":
            mapa = {"1": "Casa", "X": "Empate", "2": "Fora"}
            selecao = mapa.get(selecao, selecao)

        if nome_mercado in ["Over/Under", "Escanteios", "Cartões"]:
            linha = tabela.select_one("div.hdrtb div.fprc div:last-child")
            if linha:
                limite = linha.get_text(strip=True)
                selecao = f"{selecao} {limite}"

        mercados.append((nome_mercado, selecao, prob))

    # ===== CHAMADAS DOS MERCADOS =====
    extrair_mercado("m1x2_table", "Vitória")
    extrair_mercado("uo_table", "Over/Under")
    extrair_mercado("bts_table", "BTTS")
    extrair_mercado("corner_table", "Escanteios")
    extrair_mercado("card_table", "Cartões")

    if not mercados:
        return None

    melhor_mercado, melhor_selecao, melhor_prob = max(
        mercados, key=lambda x: x[2]
    )

    return {
        "jogo": jogo,
        "mercado": melhor_mercado,
        "selecao": melhor_selecao,
        "prob": melhor_prob,
        "url": url
    }


# ================= EXECUÇÃO =================

todos_links = []

for liga in LIGAS:
    print(f"\nAbrindo liga: {liga}")
    links = pegar_links_jogos(liga)
    print(f"Jogos encontrados: {len(links)}")
    todos_links.extend(links)

contagem = Counter(todos_links)
links_validos = [l for l in todos_links if contagem[l] == 1]

print(f"\nJogos válidos após filtro: {len(links_validos)}")

todos_palpites = []

for link in links_validos:
    dado = analisar_jogo(link)
    if dado:
        todos_palpites.append(dado)

driver.quit()

# ================= RESULTADO FINAL =================

ordenados = sorted(todos_palpites, key=lambda x: x["prob"], reverse=True)[:10]

resultado_json = {
    "data": HOJE,
    "total_picks": len(ordenados),
    "palpites": []
}

for i, p in enumerate(ordenados, start=1):
    if i <= 4:
        risco = "melhor_entrada"
    elif i <= 7:
        risco = "boa_entrada"
    else:
        risco = "mais_arriscada"

    resultado_json["palpites"].append({
        "rank": i,
        "jogo": p["jogo"],
        "mercado": p["mercado"],
        "selecao": p["selecao"],
        "probabilidade": p["prob"],
        "risco": risco,
        "url": p["url"]
    })

import json

with open("palpites.json", "w", encoding="utf-8") as f:
    json.dump(resultado_json, f, ensure_ascii=False, indent=2)

print("JSON GERADO COM SUCESSO")