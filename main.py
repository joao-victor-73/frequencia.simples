from flask import Flask, render_template
import os
import pymysql
import dotenv


# Instanciando a aplicação
app = Flask(__name__)

dotenv.load_dotenv()


# Conectar ao MySQL e abrir a conexão
connection = pymysql.connect(
    host=os.environ['MYSQL_HOST'],
    user=os.environ['MYSQL_USER'],
    password=os.environ['MYSQL_PASSWORD'],
    database=os.environ['MYSQL_DATABASE']
)

# Criando o cursor
cursor = connection.cursor()


# Rota de começo
@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')


# Rota para registrar presença
@app.route("/registrar_presenca", methods=["POST"])
def registrar_presenca():
    pass

# Rota para consultar frequência
@app.route("/frequencia", methods=["GET"])
def listar_frequencia():
    pass

if __name__ == "__main__":
    app.run(debug=True)
