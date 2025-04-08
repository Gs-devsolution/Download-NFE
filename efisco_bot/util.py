import os
import time
from datetime import datetime

def renomear_arquivo_baixado(pasta_download, cnpj_empresa, data_filtro):
    try:
        print("📦 Procurando arquivo baixado mais recente...")

        arquivos = [os.path.join(pasta_download, f) for f in os.listdir(pasta_download)]
        arquivos = sorted(arquivos, key=os.path.getmtime, reverse=True)

        if not arquivos:
            print("❌ Nenhum arquivo encontrado.")
            return

        arquivo_antigo = arquivos[0]

        # data_filtro vem no formato ddmmaaaa, vamos formatar para dd-mm-aaaa
        data_formatada = f"{data_filtro[:2]}-{data_filtro[2:4]}-{data_filtro[4:]}"
        nome_novo = f"{data_formatada}_{cnpj_empresa}.zip"
        caminho_novo = os.path.join(pasta_download, nome_novo)

        os.rename(arquivo_antigo, caminho_novo)
        print(f"✅ Arquivo renomeado para: {nome_novo}")

    except Exception as e:
        print(f"❌ Erro ao renomear arquivo: {e}")