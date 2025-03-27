import pandas as pd
from sqlalchemy import create_engine
import dotenv
import os

# Configuração do Banco de Dados (Essas configs vem do arquivo .env)
dotenv.load_dotenv()

host = os.environ['MYSQL_HOST']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
database = os.environ['MYSQL_DATABASE']

# Criar a conexão usando SQLAlchemy
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Ler a planilha Excel
df = pd.read_excel("extras_files/criacao_registros/crismandos_ficticios.xlsx")

# Ajustar o formato da data para o MySQL (YYYY-MM-DD)
df["data_nascimento"] = pd.to_datetime(
    df["data_nascimento"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")


df.columns = df.columns.str.replace(" ", "_")  # Substitui espaços por underscores


# Inserir os dados na tabela do banco de dados
df.to_sql("crismandos", con=engine, if_exists="append", index=False)

print("Dados inseridos com sucesso!")
