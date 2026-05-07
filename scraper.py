import asyncio
import concurrent.futures
import sys
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth


def _scrape_worker(produto, limite):
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="pt-BR",
        )
        page = context.new_page()
        Stealth().apply_stealth_sync(page)

        query = produto.replace(" ", "-")
        page.goto(
            f"https://lista.mercadolivre.com.br/{query}",
            timeout=60000,
            wait_until="domcontentloaded",
        )
        page.wait_for_timeout(3000)

        items = page.query_selector_all(".ui-search-layout__item")
        resultados = []

        for item in items:
            titulo_el = item.query_selector(".poly-component__title")
            preco_el  = item.query_selector(".andes-money-amount__fraction")
            link_el   = item.query_selector("a.poly-component__title")

            if not titulo_el or not preco_el:
                continue

            titulo = titulo_el.inner_text().strip()
            preco_txt = preco_el.inner_text().strip().replace(".", "").replace(",", ".")
            link = link_el.get_attribute("href").split("#")[0] if link_el else ""

            try:
                preco = float(preco_txt)
            except ValueError:
                preco = None

            resultados.append({
                "Produto buscado": produto,
                "Título": titulo,
                "Preço (R$)": preco,
                "Link": link,
            })

            if len(resultados) >= limite:
                break

        browser.close()
        return resultados


def buscar(produto, limite=10):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(_scrape_worker, produto, limite).result()
