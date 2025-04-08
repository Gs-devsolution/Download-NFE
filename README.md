# 📥 Download-NFE - Automação de Notas Fiscais no e-Fisco (PE)

Automação completa de consulta e download de Notas Fiscais Eletrônicas (NFe) no portal **e-Fisco da SEFAZ Pernambuco**, utilizando **certificado digital (.pfx)** e **resolução automática de reCAPTCHA v2** com integração à API do [AntiCaptcha](https://anti-captcha.com/).

---

## 🚀 Funcionalidades

- ✅ Instalação automática de certificados `.pfx` no repositório do Windows
- ✅ Login automático no e-Fisco via certificado digital
- ✅ Acesso à funcionalidade de "Consulta e Download de NFe"
- ✅ Preenchimento automático dos filtros de consulta:
  - Data inicial e final (dia anterior)
  - Tipo de contribuinte (`Emitente` ou `Destinatário`)
  - IE do contribuinte
- ✅ Resolução automática do reCAPTCHA v2 via API AntiCaptcha
- ✅ Consulta e validação:
  - Verifica se houve retorno de notas
  - Verifica se excedeu o limite de 500 notas
- ✅ Seleção de todas as notas retornadas
- ✅ Download automático em `.zip`
- ✅ Organização em pasta:
  - `DOWNLOADS/{CNPJ}/{dd-mm-aaaa}_{CNPJ}.zip`
- ✅ Loop de execução para múltiplas empresas (com certificados e IEs diferentes)
- ✅ Encerramento automático do navegador ao fim do processo de cada empresa

---

## 🧪 Tecnologias e Bibliotecas Utilizadas

- [Selenium](https://pypi.org/project/selenium/) - Automação do navegador
- [pyautogui](https://pypi.org/project/pyautogui/) - Simula pressionar `Enter` no seletor de certificado
- [anticaptchaofficial](https://pypi.org/project/anticaptchaofficial/) - Integração com API AntiCaptcha
- [cryptography](https://pypi.org/project/cryptography/) - Extração de informações do certificado
- [WebDriverManager](https://pypi.org/project/webdriver-manager/) - Gerencia automaticamente o driver do Chrome
- `PowerShell` (Windows) - Instala silenciosamente certificados `.pfx`

---

## 🧠 Pré-requisitos

- Python 3.10+
- Google Chrome instalado
- Certificados digitais no formato `.pfx`
- Conta na [AntiCaptcha.com](https://anti-captcha.com/) com chave de API ativa

---

## ⚙️ Como rodar

1. **Clone este repositório**
   ```bash
   git clone https://github.com/seu-usuario/Download-NFE.git
   cd Download-NFE
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure suas empresas no `main.py`**
   ```python
   empresas = [
       {
           "cert_path": r"C:\certificados\empresa1.pfx",
           "senha": "senha123",
           "ie": "123456789"
       },
       ...
   ]
   ```

4. **Adicione sua chave da API do AntiCaptcha no `main.py`**
   ```python
   chave_api = "SUA_CHAVE_API"
   ```

5. **Execute o robô**
   ```bash
   python main.py
   ```

---

## 🗂️ Estrutura de Pastas

```
efisco_bot/
├── captcha.py
├── certificado.py
├── efisco.py
├── util.py
├── main.py
```

---

## 🛡️ Observações

- Compatível apenas com Windows (uso de PowerShell para instalação do certificado).
- Sensível ao tempo de carregamento do e-Fisco.
- Certifique-se de não ter vários certificados instalados para evitar conflitos.

---

## 📌 Futuras melhorias

- Exportar resultados em Excel
- Download em lote dos arquivos XML
- Integração com e-mail para envio automático dos downloads
- Interface gráfica para uso por usuários finais
- Agendamento com `task scheduler` ou `cron` (via script externo)

---

## 🧑‍💻 Autor

Projeto criado por **[@Gs-devsolution](https://github.com/Gs-devsolution)** com apoio do [ChatGPT com GPT-4 e Selenium ❤️]
