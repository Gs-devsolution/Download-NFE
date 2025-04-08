from efisco import (
    acessar_efisco_com_certificado,
    acessar_consulta_nfe_por_busca,
    preencher_filtros,
    consultar_notas,
    ajustar_quantidade_resultados,
    selecionar_todas_as_notas,
    baixar_notas
)
from captcha import resolver_recaptcha, tem_captcha
from certificado import (
    instalar_certificado,
    remover_todos_os_certificados,
    extrair_cnpj_certificado
)
from util import renomear_arquivo_baixado

from datetime import datetime, timedelta
import time
import os


empresas = [
    {
        "cert_path": r"C:\Users\gabriel.silva\Desktop\AVILE COMERCIO & DISTRIBUIDORA LTDA - (280).pfx",
        "senha": "232523",
        "ie": "062311360"  # AVILE
    },
    {
        "cert_path": r"C:\Users\gabriel.silva\Desktop\ALBUQUERQUE HORTIFRUTIGRANJEIRO LTDA - (015).pfx",
        "senha": "123@Absoluta",
        "ie": "090569989"  # ALBUQUERQUE
    },
    {
        "cert_path": r"C:\Users\gabriel.silva\Desktop\A DE ALBUQUERQUE SOUZA HORTIFRUTIGRANJEIROS ME - (008).pfx",
        "senha": "123456",
        "ie": "056680422"  # A DE ALB
    }
]
    # AVILE = 232523 r"C:\Users\gabriel.silva\Desktop\AVILE COMERCIO & DISTRIBUIDORA LTDA - (280).pfx"
    # ALBUQUERQUE = 123@Absoluta r"C:\Users\gabriel.silva\Desktop\ALBUQUERQUE HORTIFRUTIGRANJEIRO LTDA - (015).pfx"
    # A DE ALB = 123456 r"C:\Users\gabriel.silva\Desktop\A DE ALBUQUERQUE SOUZA HORTIFRUTIGRANJEIROS ME - (008).pfx"

def executar_fluxo_efisco(cert_path, senha_certificado, ie_emitente):
    # 📆 Data padrão (dia anterior)
    ontem = datetime.now() - timedelta(days=1)
    data_inicial = data_final = ontem.strftime("%d%m%Y")

    # 📁 Pasta padrão
    pasta_downloads = r"C:\Users\gabriel.silva\Downloads"

    # 🔐 Certificados
    remover_todos_os_certificados()
    if not instalar_certificado(cert_path, senha_certificado):
        print("❌ Certificado não foi instalado.")
        return

    cnpj = extrair_cnpj_certificado(cert_path, senha_certificado)
    if not cnpj:
        print("❌ Não foi possível extrair o CNPJ.")
        return

    tipo_contribuinte = "E"
    chave_api = "04ef342062f33c2fb04f3d8ece324f25"
    pasta_base_downloads = os.path.join(os.getcwd(), "DOWNLOADS")

    pasta_downloads_empresa = os.path.join(pasta_base_downloads, cnpj)
    os.makedirs(pasta_downloads_empresa, exist_ok=True)


    
    driver = acessar_efisco_com_certificado(pasta_downloads_empresa)
    if not driver:
        print("❌ Falha ao iniciar navegador.")
        return

    try:
        if not acessar_consulta_nfe_por_busca(driver):
            return

        if not preencher_filtros(driver, data_inicial, data_final, tipo_contribuinte, ie_emitente):
            return

        if tem_captcha(driver):
            if not resolver_recaptcha(driver, chave_api):
                return

        status_consulta = consultar_notas(driver)

        if status_consulta == "EXCESSO":
            return
        if status_consulta == "VAZIO":
            return

        ajustar_quantidade_resultados(driver)

        if not selecionar_todas_as_notas(driver):
            return
        if not baixar_notas(driver, pasta_downloads_empresa):
            return

        renomear_arquivo_baixado(pasta_downloads_empresa, cnpj, data_inicial)
        print("✅ Processo concluído com sucesso.")

    finally:
        print("🧹 Encerrando navegador da empresa atual...")
        driver.quit()

if __name__ == "__main__":
    for empresa in empresas:
        print(f"\n🚀 Iniciando processo para: {empresa['cert_path']}")
        executar_fluxo_efisco(
            cert_path=empresa["cert_path"],
            senha_certificado=empresa["senha"],
            ie_emitente=empresa["ie"]
        )
        print("⏸️ Aguardando 5 segundos antes de continuar...")
        time.sleep(5)
