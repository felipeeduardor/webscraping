from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def buscar_precos(produto, limite=10):
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
        page.goto(f"https://lista.mercadolivre.com.br/{query}", timeout=30000)
        page.wait_for_timeout(5000)

        items = page.query_selector_all(".ui-search-layout__item")

        print(f"\n{'='*60}")
        print(f"  Preços de '{produto}' no Mercado Livre")
        print(f"{'='*60}\n")

        encontrados = 0
        for item in items:
            titulo_el = item.query_selector(".poly-component__title")
            preco_el  = item.query_selector(".andes-money-amount__fraction")
            link_el   = item.query_selector("a.poly-component__title")

            if not titulo_el or not preco_el:
                continue

            titulo = titulo_el.inner_text().strip()
            preco  = preco_el.inner_text().strip()
            link   = link_el.get_attribute("href") if link_el else "N/A"

            # pega só a URL limpa antes dos parâmetros de rastreamento
            link_limpo = link.split("#")[0] if link != "N/A" else "N/A"

            print(f"[{encontrados+1}] {titulo}")
            print(f"    Preço : R$ {preco}")
            print(f"    Link  : {link_limpo}")
            print()
            encontrados += 1

            if encontrados >= limite:
                break

        browser.close()

        if encontrados == 0:
            print("Nenhum resultado encontrado.")

if __name__ == "__main__":
    entrada = input("Buscar produtos (separe por vírgula): ").strip()
    produtos = [p.strip() for p in entrada.split(",") if p.strip()]
    if not produtos:
        produtos = ["notebook"]
    for produto in produtos:
        buscar_precos(produto)
