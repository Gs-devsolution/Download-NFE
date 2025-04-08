from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from anticaptchaofficial.recaptchav2proxyless import *
import time
import pyautogui
import threading
from selenium.webdriver.support.ui import Select
import os
import time
from datetime import datetime
import glob


def executar_fluxo_efisco():
    cnpj = "12345678000195"
    caminho_download = "C:\\Users\\SEU_USUARIO\\Downloads"
    chave_api = "04ef342062f33c2fb04f3d8ece324f25"

    driver = acessar_efisco_com_certificado()
    if driver:
        acessar_consulta_nfe_por_busca(driver, chave_api, caminho_download, cnpj)
    else:
        print("❌ Falha ao iniciar navegador.")

def acessar_efisco_com_certificado():
    try:
        print("🌐 Acessando o site do e-Fisco...")

        options = Options()
        options.add_argument("--start-maximized")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://efisco.sefaz.pe.gov.br/sfi_com_sca/PRMontarMenuAcesso")
        
        def pressionar_enter():
            time.sleep(2)  # Tempo para a janela do certificado abrir
            print("✅ Pressionando Enter no seletor de certificado...")
            pyautogui.press("enter")

        # Inicia thread para pressionar Enter
        threading.Thread(target=pressionar_enter).start()

        # Clica no botão de certificado
        wait = WebDriverWait(driver, 20)
        botao_cert = wait.until(EC.element_to_be_clickable((By.ID, 'btt_certificado')))

        botao_cert.click()
        print("🖱️ Botão 'Certificado Digital' clicado.")

        # Chama a função para navegar até a aba de NFe
        acessar_consulta_nfe_por_busca(driver)

        return driver

    except Exception as e:
        print(f"❌ Erro ao acessar o e-Fisco: {e}")
        return None

def acessar_consulta_nfe_por_busca(driver, chave_api, caminho_download, cnpj):
    wait = WebDriverWait(driver, 20)
    try:
        print("⌛ Aguardando página logada carregar após login com certificado...")
        time.sleep(5)

        print("🔍 Clicando no campo de busca principal...")
        campo_busca = wait.until(EC.element_to_be_clickable((By.ID, "input_busca_geral")))
        campo_busca.click()

        print("⌛ Aguardando campo de digitação aparecer...")
        campo_modal = wait.until(EC.element_to_be_clickable((By.ID, "input_busca_geral_interno")))
        campo_modal.clear()
        campo_modal.send_keys("Consulta e Download de NFe (#)")

        print("🔎 Clicando no botão de busca...")
        botao_busca = wait.until(EC.element_to_be_clickable((By.ID, "botao_busca")))
        botao_busca.click()

        print("📄 Clicando no link do resultado...")
        resultado = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Consulta e Download de NFe')]")))
        resultado.click()

        print("🪟 Aguardando nova janela abrir...")
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[-1])
        print("✅ Nova janela da NFe ativa!")

        # Inicia consulta
        preencher_filtros_e_consultar(driver, chave_api, caminho_download, cnpj)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Erro ao buscar e acessar a funcionalidade: {e}")


def resolver_recaptcha(driver, chave_api, max_tentativas=3):
    try:
        print("🔍 Buscando sitekey...")
        sitekey_element = driver.find_element(By.CLASS_NAME, 'g-recaptcha')
        sitekey = sitekey_element.get_attribute('data-sitekey')

        solver = recaptchaV2Proxyless()
        solver.set_verbose(1)
        solver.set_key(chave_api)
        solver.set_website_url(driver.current_url)
        solver.set_website_key(sitekey)

        tentativa = 0
        while tentativa < max_tentativas:
            print(f"🤖 Tentativa {tentativa + 1} de resolução do CAPTCHA...")

            token = solver.solve_and_return_solution()
            if token == 0:
                print(f"❌ Falha no AntiCaptcha: {solver.err_string}")
                return False

            print("✅ Token resolvido! Inserindo na página...")

            driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{token}'")

            # Clica no botão consultar
            driver.find_element(By.ID, 'consultar').click()
            time.sleep(3)

            # Verifica se deu erro de captcha inválido
            if "Captcha inválido" in driver.page_source:
                print("❌ CAPTCHA inválido detectado. Tentando novamente...")
                tentativa += 1
                continue
            else:
                print("✅ CAPTCHA aceito!")
                return True

        print("🚫 Limite de tentativas atingido. CAPTCHA não resolvido.")
        return False

    except Exception as e:
        print(f"❌ Erro ao resolver captcha: {e}")
        return False

def tem_captcha(driver):
    try:
        elementos = driver.find_elements(By.CLASS_NAME, 'g-recaptcha')
        if len(elementos) > 0:
            print("🛑 reCAPTCHA encontrado na página.")
            return True
        else:
            print("✅ Nenhum reCAPTCHA encontrado.")
            return False
    except Exception as e:
        print(f"⚠️ Erro ao verificar captcha: {e}")
        return False

def ajustar_quantidade_resultados(driver):
    try:
        wait = WebDriverWait(driver, 10)
        print("🔄 Buscando seletor de quantidade de resultados...")

        seletor = wait.until(EC.presence_of_element_located((By.NAME, "pages")))

        # Verifica se o valor 500 já está presente
        opcoes = seletor.find_elements(By.TAG_NAME, "option")
        valores = [op.get_attribute("value") for op in opcoes]

        if "500" not in valores:
            print("➕ Inserindo opção 500 no seletor via JavaScript...")
            driver.execute_script("""
                let select = arguments[0];
                let option = document.createElement("option");
                option.value = "500";
                option.text = "500";
                select.appendChild(option);
            """, seletor)

        # Seleciona o valor 500
        Select(seletor).select_by_value("500")
        print("✅ Seletor ajustado para 500 registros por página.")

        # Clica novamente em "Consultar"
        botao_consultar = wait.until(EC.element_to_be_clickable((By.ID, "consultar")))
        botao_consultar.click()
        print("🔁 Consulta reenviada com novo limite.")

    except Exception as e:
        print(f"⚠️ Erro ao ajustar quantidade de resultados: {e}")

def selecionar_todas_e_baixar(driver):
    try:
        wait = WebDriverWait(driver, 10)

        # 1. Selecionar a checkbox "lista" (seleciona todas)
        print("🟩 Selecionando checkbox 'lista' para marcar todas as notas...")
        checkbox_lista = wait.until(EC.element_to_be_clickable((By.ID, "lista")))
        checkbox_lista.click()

        # 2. Clicar no botão de download
        print("⬇️ Clicando no botão de download das NF-es...")
        botao_download = wait.until(EC.element_to_be_clickable((By.ID, "download")))
        botao_download.click()

        print("✅ Download iniciado com sucesso!")

    except Exception as e:
        print(f"⚠️ Erro ao selecionar ou baixar as notas: {e}")

def renomear_arquivo_download(caminho_pasta, cnpj_empresa):
    try:
        print("⏳ Aguardando o término do download...")

        # Espera pelo arquivo .crdownload ser concluído (arquivo do Chrome em download)
        timeout = time.time() + 60  # 1 minuto máx.
        while True:
            arquivos_em_progresso = glob.glob(os.path.join(caminho_pasta, "*.crdownload"))
            if not arquivos_em_progresso:
                break
            if time.time() > timeout:
                print("⚠️ Tempo limite atingido esperando o download.")
                return
            time.sleep(1)

        # Encontra o arquivo mais recente baixado
        arquivos = sorted(
            [os.path.join(caminho_pasta, f) for f in os.listdir(caminho_pasta)],
            key=os.path.getmtime,
            reverse=True
        )
        if not arquivos:
            print("⚠️ Nenhum arquivo encontrado para renomear.")
            return

        arquivo_antigo = arquivos[0]

        # Monta nome novo
        hoje = datetime.now()
        dia = hoje.strftime("%d")
        ano = hoje.strftime("%Y")
        nome_novo = f"{dia}-{ano}_{cnpj_empresa}.zip"
        caminho_novo = os.path.join(caminho_pasta, nome_novo)

        os.rename(arquivo_antigo, caminho_novo)
        print(f"✅ Arquivo renomeado para: {nome_novo}")

    except Exception as e:
        print(f"❌ Erro ao renomear arquivo: {e}")

def preencher_filtros_e_consultar(driver, chave_api, caminho_download, cnpj):
    wait = WebDriverWait(driver, 20)

    try:
        print("🗓️ Preenchendo data inicial...")
        data_inicial = wait.until(EC.element_to_be_clickable((By.NAME, "dataIni")))
        data_inicial.clear()
        data_inicial.send_keys("02012025")

        print("🗓️ Preenchendo data final...")
        data_final = wait.until(EC.element_to_be_clickable((By.NAME, "dataFim")))
        data_final.clear()
        data_final.send_keys("02012025")

        print("✅ Selecionando 'Emitente'...")
        botao_emitente = wait.until(EC.element_to_be_clickable((By.ID, "tipoContrib")))
        botao_emitente.click()

        print("🧾 Preenchendo IE Emitente...")
        ie_input = wait.until(EC.element_to_be_clickable((By.NAME, "ieEmitente")))
        ie_input.clear()
        ie_input.send_keys("056680422")

        if tem_captcha(driver):
            print("🤖 Resolvendo reCAPTCHA...")
            if resolver_recaptcha(driver, chave_api):
                print("🔓 CAPTCHA resolvido com sucesso!")
            else:
                print("⚠️ CAPTCHA não foi resolvido.")
        else:
            print("⏩ Nenhum CAPTCHA para resolver. Pulando etapa.")

        ajustar_quantidade_resultados(driver)
        selecionar_todas_e_baixar(driver)
        renomear_arquivo_download(caminho_download, cnpj)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Erro ao preencher filtros ou consultar: {e}")


# ===== EXECUÇÃO =====
driver = acessar_efisco_com_certificado()


# Aqui você pode seguir a automação na página de NFe (ex: preenchimento de filtros)
