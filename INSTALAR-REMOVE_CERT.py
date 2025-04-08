import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def instalar_certificado_interativamente():
    """
    Abre interface gráfica para o usuário selecionar um certificado .pfx,
    digitar a senha e instala o certificado no repositório pessoal do usuário.
    """
    def instalar_certificado(pfx_path, senha):
        try:
            comando = [
                "powershell",
                "-Command",
                f"Import-PfxCertificate -FilePath '{pfx_path}' -CertStoreLocation 'Cert:\\CurrentUser\\My' -Password (ConvertTo-SecureString '{senha}' -AsPlainText -Force)"
            ]

            resultado = subprocess.run(comando, capture_output=True, text=True)

            if resultado.returncode == 0:
                return True, resultado.stdout
            else:
                return False, resultado.stderr or resultado.stdout

        except Exception as e:
            return False, str(e)

    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal

    try:
        # 1. Selecionar o certificado
        pfx_path = filedialog.askopenfilename(
            title="Selecione o certificado .pfx",
            filetypes=[("Certificado PFX", "*.pfx")]
        )

        if not pfx_path:
            messagebox.showerror("Erro", "Nenhum certificado foi selecionado.")
            return False

        # 2. Digitar senha
        senha = simpledialog.askstring("Senha do certificado", "Digite a senha do certificado:", show="*")
        if not senha:
            messagebox.showerror("Erro", "Senha não informada.")
            return False

        # 3. Instalar certificado
        sucesso, saida = instalar_certificado(pfx_path, senha)

        if sucesso:
            messagebox.showinfo("Sucesso", "✅ Certificado instalado com sucesso!")
            return True
        else:
            messagebox.showerror("Erro na instalação", f"❌ Ocorreu um erro ao instalar o certificado:\n\n{saida}")
            return False

    except Exception as geral:
        messagebox.showerror("Erro inesperado", f"Ocorreu um erro inesperado:\n\n{str(geral)}")
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

