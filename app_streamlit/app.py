import io
import concurrent.futures
import pandas as pd
import streamlit as st
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

st.set_page_config(page_title="Buscador ML", page_icon="🛍️", layout="wide")
st.title("🛍️ Buscador de Preços — Mercado Livre")
st.caption("Digite os produtos separados por vírgula e clique em Buscar.")

col1, col2 = st.columns([4, 1])
with col1:
    entrada = st.text_input("Produtos", placeholder="notebook, iphone 15, headphone")
with col2:
    limite = st.number_input("Resultados por produto", min_value=1, max_value=30, value=10)

buscar = st.button("🔍 Buscar", use_container_width=True)


def _scrape_worker(produto, limite):
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
        resultados = []

        for item in items:
            titulo_el = item.query_selector(".poly-component__title")
            preco_el  = item.query_selector(".andes-money-amount__fraction")
            link_el   = item.query_selector("a.poly-component__title")

            if not titulo_el or not preco_el:
                continue

            titulo = titulo_el.inner_text().strip()
            preco_txt = preco_el.inner_text().strip().replace(".", "").replace(",", ".")
            link  = link_el.get_attribute("href").split("#")[0] if link_el else ""

            try:
                preco = float(preco_txt)
            except ValueError:
                preco = None

            resultados.append({"Produto buscado": produto, "Título": titulo, "Preço (R$)": preco, "Link": link})

            if len(resultados) >= limite:
                break

        browser.close()
        return resultados


def scrape(produto, limite):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(_scrape_worker, produto, limite).result()


if buscar and entrada.strip():
    produtos = [p.strip() for p in entrada.split(",") if p.strip()]
    todos = []

    for produto in produtos:
        with st.spinner(f"Buscando **{produto}**..."):
            resultados = scrape(produto, limite)
            todos.extend(resultados)

    if todos:
        df = pd.DataFrame(todos)

        for produto in produtos:
            sub = df[df["Produto buscado"] == produto].reset_index(drop=True)
            st.subheader(f"📦 {produto.title()}")

            st.dataframe(
                sub[["Título", "Preço (R$)", "Link"]],
                use_container_width=True,
                column_config={
                    "Link": st.column_config.LinkColumn("Link"),
                    "Preço (R$)": st.column_config.NumberColumn("Preço (R$)", format="R$ %.2f"),
                },
            )

            menor = sub["Preço (R$)"].min()
            maior = sub["Preço (R$)"].max()
            st.caption(f"Menor: R$ {menor:,.2f} | Maior: R$ {maior:,.2f}")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for produto in produtos:
                sub = df[df["Produto buscado"] == produto]
                sheet = produto[:31]
                sub.to_excel(writer, sheet_name=sheet, index=False)
        buffer.seek(0)

        st.download_button(
            label="📥 Baixar Excel",
            data=buffer,
            file_name="precos_ml.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    else:
        st.warning("Nenhum resultado encontrado.")
