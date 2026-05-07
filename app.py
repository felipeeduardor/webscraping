import io
import pandas as pd
import streamlit as st
from scraper import buscar

st.set_page_config(page_title="Buscador ML", page_icon="🛍️", layout="wide")
st.title("🛍️ Buscador de Preços — Mercado Livre")
st.caption("Digite os produtos separados por vírgula e clique em Buscar.")

col1, col2 = st.columns([4, 1])
with col1:
    entrada = st.text_input("Produtos", placeholder="notebook, iphone 15, headphone")
with col2:
    limite = st.number_input("Resultados por produto", min_value=1, max_value=30, value=10)

if st.button("🔍 Buscar", use_container_width=True) and entrada.strip():
    produtos = [p.strip() for p in entrada.split(",") if p.strip()]
    todos = []

    for produto in produtos:
        with st.spinner(f"Buscando **{produto}**..."):
            todos.extend(buscar(produto, limite))

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
                sub.to_excel(writer, sheet_name=produto[:31], index=False)
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
