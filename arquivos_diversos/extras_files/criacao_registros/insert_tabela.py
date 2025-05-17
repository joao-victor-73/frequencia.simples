import pandas as pd
from sqlalchemy import create_engine
import dotenv
import os


def remove_acentos(valor):
    if pd.isna(valor):
        return None
    valor = str(valor).lower()
    valor = valor.replace("não", "nao")
    valor = valor.replace("não sei", "nao sei")
    valor = valor.strip().capitalize()
    return valor

# Configuração do Banco de Dados (Essas configs vem do arquivo .env)
dotenv.load_dotenv()

host = os.environ['MYSQL_HOST']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
database = os.environ['MYSQL_DATABASE']
port = os.environ['MYSQL_PORT']

# Criar a conexão usando SQLAlchemy
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")


# Caminho absoluto do diretório onde o script está
base_dir = os.path.dirname(os.path.abspath(__file__))

# Monta o caminho completo do Excel
file_path = os.path.join(base_dir, "inscritos.xlsx")



# Ler a planilha Excel
df = pd.read_excel(file_path, sheet_name="Respostas - em tratamento")

# Ajustar o formato da data para o MySQL (YYYY-MM-DD)
df["data_nascimento"] = pd.to_datetime(df["data_nascimento"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")

# Removendo acentuação de respostas Enum
df["batismo"] = df["batismo"].apply(remove_acentos)
df["eucaristia"] = df["eucaristia"].apply(remove_acentos)
df["possui_deficiencia"] = df["possui_deficiencia"].apply(remove_acentos)
df["possui_filhos"] = df["possui_filhos"].apply(remove_acentos)


# Substitui espaços por underscores
df.columns = df.columns.str.replace(" ", "_")  

# Inserir os dados na tabela do banco de dados
df.to_sql("crismandos", con=engine, if_exists="append", index=False)

print(f"{len(df)} registros foram inseridos na tabela 'crismandos'.")
print("Dados inseridos com sucesso!")
