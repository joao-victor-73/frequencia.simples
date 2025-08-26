import os
from dotenv import load_dotenv
import subprocess
import smtplib
import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

load_dotenv()

# 🔹 Configurações do banco MySQL
DB_HOST = os.environ['MYSQL_HOST']
DB_USER = os.environ['MYSQL_USER']
DB_PASS = os.environ['MYSQL_PASSWORD']
DB_NAME = os.environ['MYSQL_DATABASE']
DB_PORT = os.environ['MYSQL_PORT']


# 🔹 Configurações do e-mail
EMAIL_ORIGEM = os.environ['MAIL_USERNAME']
EMAIL_SENHA = os.environ['MAIL_PASSWORD']  # usar senha de app do Gmail
# EMAIL_DESTINO = os.environ['MAIL_RECIPIENTS']  # Email para quem vai ser enviado


def gerar_backup():
    """Gera backup do banco MySQL"""

    # Criar a pasta se não existir
    os.makedirs("backups", exist_ok=True)

    data = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    nome_arquivo = os.path.join("backups", f"backup_{data}.sql")

    comando = [
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
        f"-h{DB_HOST}",
        f"-P{DB_PORT}",
        f"-u{DB_USER}",
        f"-p{DB_PASS}",
        "--protocol=TCP",
        DB_NAME
    ]

     # Executa o comando e salva no arquivo
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        result = subprocess.run(comando, stdout=f, stderr=subprocess.PIPE, text=True)
        if result.stderr:
            print("⚠️ Erro no mysqldump:", result.stderr)

    return nome_arquivo


def enviar_email(arquivo_backup):
    """Envia o backup por e-mail"""


    destinatarios = os.environ["MAIL_RECIPIENTS"].split(",")

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ORIGEM
    msg["To"] = ", ".join(destinatarios)  # cabeçalho To
    msg["Subject"] = "Backup Automático do Sistema"

    corpo = "Olá!. Segue em anexo o backup semanal do banco de dados do sistema da crisma."
    msg.attach(MIMEText(corpo, "plain"))

    # Anexar o arquivo
    with open(arquivo_backup, "rb") as anexo:
        mime = MIMEBase("application", "octet-stream")
        mime.set_payload(anexo.read())
        encoders.encode_base64(mime)
        mime.add_header("Content-Disposition",
                        f"attachment; filename={arquivo_backup}")
        msg.attach(mime)

    # Envio via SMTP
    with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
        servidor.starttls()
        servidor.login(EMAIL_ORIGEM, EMAIL_SENHA)
        servidor.send_message(msg, from_addr=EMAIL_ORIGEM, to_addrs=destinatarios)

    print(f"✅ Backup enviado para {', '.join(destinatarios)}")



if __name__ == "__main__":
    backup = gerar_backup()
    enviar_email(backup)
