from selenium.webdriver.common.by import By
import time
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

def tem_captcha(driver):
    try:
        elementos = driver.find_elements(By.CLASS_NAME, 'g-recaptcha')
        if len(elementos) > 0:
            print("🛑 reCAPTCHA detectado na página.")
            return True
        print("✅ Nenhum reCAPTCHA detectado.")
        return False
    except Exception as e:
        print(f"⚠️ Erro ao verificar presença do reCAPTCHA: {e}")
        return False

def resolver_recaptcha(driver, chave_api, max_tentativas=3):
    try:
        print("🔍 Buscando sitekey para o reCAPTCHA...")
        sitekey_element = driver.find_element(By.CLASS_NAME, 'g-recaptcha')
        sitekey = sitekey_element.get_attribute('data-sitekey')

        solver = recaptchaV2Proxyless()
        solver.set_verbose(1)
        solver.set_key(chave_api)
        solver.set_website_url(driver.current_url)
        solver.set_website_key(sitekey)

        tentativa = 1
        while tentativa <= max_tentativas:
            print(f"🤖 Tentativa {tentativa} de resolução...")

            token = solver.solve_and_return_solution()
            if token == 0:
                print(f"❌ Falha no AntiCaptcha: {solver.err_string}")
                return False

            print("✅ Token resolvido! Inserindo na página...")
            driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{token}'")

            # Clica no botão "Consultar"
            driver.find_element(By.ID, 'consultar').click()
            time.sleep(3)

            # Verifica se o CAPTCHA foi aceito
            if "Captcha inválido" in driver.page_source:
                print("🚫 CAPTCHA inválido. Nova tentativa...")
                tentativa += 1
                continue
            else:
                print("🔓 CAPTCHA resolvido e aceito!")
                return True

        print("❌ Todas as tentativas falharam.")
        return False

    except Exception as e:
        print(f"❌ Erro ao resolver reCAPTCHA: {e}")
        return False
