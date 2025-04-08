import subprocess
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend

def extrair_cnpj_certificado(pfx_path, senha):
    try:
        with open(pfx_path, "rb") as f:
            pfx_data = f.read()

        _, certificate, _ = pkcs12.load_key_and_certificates(
            pfx_data,
            senha.encode(),
            backend=default_backend()
        )

        subject = certificate.subject

        # Extrai o CN e divide pelos dois-pontos
        for attribute in subject:
            if attribute.oid.dotted_string == "2.5.4.3":  # Common Name (CN)
                cn = attribute.value
                partes = cn.split(":")
                if len(partes) == 2:
                    return partes[1].strip()  # Retorna o CNPJ limpo
                else:
                    print("⚠️ Common Name não está no formato esperado com dois-pontos.")
                    return None

        print("⚠️ Common Name não encontrado no certificado.")
        return None

    except Exception as e:
        print(f"❌ Erro ao extrair CNPJ do certificado: {e}")
        return None


def instalar_certificado(pfx_path, senha):
    try:
        print(f"🔐 Instalando certificado: {pfx_path}")
        comando = [
            "powershell",
            "-Command",
            f"Import-PfxCertificate -FilePath '{pfx_path}' -CertStoreLocation 'Cert:\\CurrentUser\\My' -Password (ConvertTo-SecureString '{senha}' -AsPlainText -Force)"
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True)

        if resultado.returncode == 0:
            print("✅ Certificado instalado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao instalar certificado:\n{resultado.stderr}")
            return False

    except Exception as e:
        print(f"❌ Erro inesperado ao instalar certificado: {e}")
        return False

def remover_todos_os_certificados():
    comando = [
        "powershell",
        "-Command",
        """
        $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("My","CurrentUser");
        $store.Open("ReadWrite");
        foreach ($cert in $store.Certificates) {
            $store.Remove($cert);
        }
        $store.Close();
        Write-Output '✅ Todos os certificados foram removidos com sucesso.';
        """
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    print(resultado.stdout or resultado.stderr)
