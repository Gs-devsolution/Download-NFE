from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
import threading
import time
import glob
import os

# ===== LOGIN COM CERTIFICADO =====

def acessar_efisco_com_certificado(pasta_download):
    try:
        options = Options()
        prefs = {
            "download.default_directory": pasta_download,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--start-maximized")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://efisco.sefaz.pe.gov.br/sfi_com_sca/PRMontarMenuAcesso")

        def pressionar_enter():
            time.sleep(2)
            print("✅ Pressionando Enter no seletor de certificado...")
            pyautogui.press("enter")

        threading.Thread(target=pressionar_enter).start()

        wait = WebDriverWait(driver, 20)
        botao_cert = wait.until(EC.element_to_be_clickable((By.ID, 'btt_certificado')))
        botao_cert.click()
        print("🖱️ Botão 'Certificado Digital' clicado.")
        return driver

    except Exception as e:
        print(f"❌ Erro ao acessar o e-Fisco: {e}")
        return None

# ===== NAVEGAÇÃO ATÉ A ABA DE NFe =====

def acessar_consulta_nfe_por_busca(driver):
    wait = WebDriverWait(driver, 20)

    try:
        print("⌛ Aguardando carregamento após login...")
        time.sleep(5)

        print("🔍 Buscando funcionalidade 'Consulta e Download de NFe'...")
        campo_busca = wait.until(EC.element_to_be_clickable((By.ID, "input_busca_geral")))
        campo_busca.click()

        campo_modal = wait.until(EC.element_to_be_clickable((By.ID, "input_busca_geral_interno")))
        campo_modal.clear()
        campo_modal.send_keys("Consulta e Download de NFe (#)")

        botao_busca = wait.until(EC.element_to_be_clickable((By.ID, "botao_busca")))
        botao_busca.click()

        resultado = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Consulta e Download de NFe')]")))
        resultado.click()

        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[-1])
        print("✅ Aba de Consulta de NFe carregada.")
        return True

    except Exception as e:
        print(f"❌ Erro ao acessar a funcionalidade: {e}")
        return False

# ===== PREENCHIMENTO DE FILTROS =====

def preencher_filtros(driver, data_ini, data_fim, tipo_contrib, ie):
    wait = WebDriverWait(driver, 20)
    try:
        print("🧾 Preenchendo filtros da consulta...")

        data_inicial = wait.until(EC.element_to_be_clickable((By.NAME, "dataIni")))
        data_inicial.clear()
        data_inicial.send_keys(data_ini)

        data_final = wait.until(EC.element_to_be_clickable((By.NAME, "dataFim")))
        data_final.clear()
        data_final.send_keys(data_fim)

        # Seleciona Emitente ou Destinatário
        input_radio = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[@name='tipoContrib'][@value='{tipo_contrib}']")))
        input_radio.click()

        ie_emitente = wait.until(EC.element_to_be_clickable((By.NAME, "ieEmitente")))
        ie_emitente.clear()
        ie_emitente.send_keys(ie)

        print("✅ Filtros preenchidos.")
        return True

    except Exception as e:
        print(f"❌ Erro ao preencher filtros: {e}")
        return False

# ===== CONSULTA =====

def consultar_notas(driver):
    try:
        wait = WebDriverWait(driver, 15)
        print("🔍 Clicando em 'Consultar'...")

        botao_consultar = wait.until(EC.element_to_be_clickable((By.ID, "consultar")))
        botao_consultar.click()

        # Aguarda ou mensagem ou resultado aparecer
        time.sleep(3)  # pequeno delay para garantir renderização do DOM

        # Verifica se aparece a mensagem de mais de 500 registros
        if "A consulta resultou em mais de 500 registros" in driver.page_source:
            print("❌ Consulta excedeu o limite de 500 registros. Refine o período.")
            return "EXCESSO"

        # Verifica se não há resultados
        if "Não foram encontrados itens no banco de dados para a consulta" in driver.page_source:
            print("⚠️ Nenhuma nota encontrada para o filtro informado.")
            return "VAZIO"

        print("✅ Consulta realizada com sucesso.")
        return "OK"

    except Exception as e:
        print(f"❌ Erro ao consultar notas: {e}")
        return "ERRO"

# ===== AJUSTAR QUANTIDADE DE RESULTADOS PARA 500 =====

def ajustar_quantidade_resultados(driver):
    try:
        print("🔄 Ajustando quantidade de resultados para 500...")

        wait = WebDriverWait(driver, 20)

        seletor = wait.until(EC.presence_of_element_located((By.NAME, "pages")))

        # Verifica se a opção "500" já existe
        opcoes = seletor.find_elements(By.TAG_NAME, "option")
        valores = [op.get_attribute("value") for op in opcoes]

        if "500" not in valores:
            print("➕ Inserindo valor 500 manualmente via JS...")
            driver.execute_script("""
                let select = arguments[0];
                let option = document.createElement("option");
                option.value = "500";
                option.text = "500";
                select.appendChild(option);
            """, seletor)
            time.sleep(0.5)

        # Seleciona o valor 500
        from selenium.webdriver.support.ui import Select
        Select(seletor).select_by_value("500")
        print("✅ Valor 500 selecionado.")

        # Espera o botão aparecer de novo e ficar clicável
        print("⌛ Aguardando botão 'Consultar' reaparecer...")
        botao_consultar = wait.until(EC.element_to_be_clickable((By.ID, "consultar")))

        botao_consultar.click()
        print("🔁 Consulta reenviada com 500 registros por página.")

        # Aguarda carregamento dos resultados (simples delay)
        time.sleep(2)

    except Exception as e:
        print(f"⚠️ Erro ao ajustar quantidade de resultados: {e}")

# ===== SELECIONAR NOTAS E BAIXAR =====

def selecionar_todas_as_notas(driver):
    try:
        wait = WebDriverWait(driver, 10)
        print("☑️ Selecionando todas as notas...")

        checkbox_lista = wait.until(EC.element_to_be_clickable((By.ID, "lista")))
        checkbox_lista.click()
        return True

    except Exception as e:
        print(f"❌ Erro ao selecionar notas: {e}")
        return False

def baixar_notas(driver, pasta_download):
    try:
        wait = WebDriverWait(driver, 10)
        print("⬇️ Clicando em download das notas...")

        # 🕐 Captura os arquivos .zip existentes antes de clicar
        arquivos_antes = set(glob.glob(os.path.join(pasta_download, "*.zip")))

        botao_download = wait.until(EC.element_to_be_clickable((By.ID, "download")))
        botao_download.click()
        print("✅ Download iniciado. Aguardando finalização...")

        # Espera até um novo arquivo aparecer (timeout de 20s)
        timeout = 20
        start_time = time.time()

        while time.time() - start_time < timeout:
            arquivos_atuais = set(glob.glob(os.path.join(pasta_download, "*.zip")))
            novos = arquivos_atuais - arquivos_antes
            if novos:
                print("✅ Download finalizado.")
                return True
            time.sleep(0.5)

        print("⚠️ Tempo esgotado: Nenhum novo arquivo detectado.")
        return False

    except Exception as e:
        print(f"❌ Erro ao baixar notas: {e}")
        return False

def aguardar_download_iniciar_e_finalizar(pasta_downloads, timeout=120):
    print("⏳ Aguardando o início do download...")
    fim = time.time() + timeout

    # Etapa 1 – Espera aparecer .crdownload
    while time.time() < fim:
        arquivos_temp = glob.glob(os.path.join(pasta_downloads, "*.crdownload"))
        if arquivos_temp:
            print("📥 Download iniciado.")
            break
        time.sleep(1)
    else:
        print("⚠️ O download não foi iniciado dentro do tempo limite.")
        return False

    # Etapa 2 – Espera sumir .crdownload (download finalizado)
    print("⌛ Aguardando o término do download...")
    while time.time() < fim:
        arquivos_temp = glob.glob(os.path.join(pasta_downloads, "*.crdownload"))
        if not arquivos_temp:
            print("✅ Download finalizado.")
            return True
        time.sleep(1)

    print("⚠️ O download não foi concluído dentro do tempo limite.")
    return False