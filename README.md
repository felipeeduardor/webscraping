# Buscador de Preços — Mercado Livre

Ferramenta web para buscar e comparar preços no Mercado Livre em tempo real, com exportação para Excel.

## Demo

https://github.com/felipeeduardor/webscraping/blob/master/demo.mp4

## Funcionalidades

- Busca múltiplos produtos de uma vez (separados por vírgula)
- Exibe título, preço e link de cada anúncio
- Mostra o menor e maior preço encontrado
- Exporta os resultados para planilha Excel

## Tecnologias

- [Streamlit](https://streamlit.io/) — interface web
- [Playwright](https://playwright.dev/python/) — scraping com navegador real
- [Pandas](https://pandas.pydata.org/) — manipulação dos dados
- [OpenPyXL](https://openpyxl.readthedocs.io/) — geração do Excel

## Como rodar

```bash
pip install -r requirements.txt
playwright install chromium
streamlit run app.py
```

Acesse em `http://localhost:8501`
