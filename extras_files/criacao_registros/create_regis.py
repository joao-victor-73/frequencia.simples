
"""
Pequeno Script para a criação de registros ficticios para eu fazer uma prática no meu pequeno
projeto. Utilizei o Chatgpt para me orientar quais bibliotecas utilizar e para pequenas
correções onde eu errei e ou quando não sabia como fazer.
"""

import pandas as pd
import random
from faker import Faker

# pip freeze
# pip uninstall o.nome.do.pacote.que.voce.quer.remover


fake = Faker("pt_BR")

# Opções para os campos específicos
cidades = ["Conde", "Alhandra", "Mata Redonda"]
sim_nao = ["sim", "nao"]
status = ["ativo", "desistente"]
ids_catequista = [1, 2]

# Criar lista de registros
dados = []
for _ in range(55):  # Mais de 50 registros
    nome = fake.name()
    nome_mae = fake.name_female()
    nome_pai = fake.name_male()
    data_nascimento = fake.date_of_birth(minimum_age=12, maximum_age=20).strftime("%d/%m/%Y")
    endereco = fake.street_address()
    cidade = random.choice(cidades)
    telefone1 = fake.phone_number()
    telefone2 = fake.phone_number() if random.choice([True, False]) else None
    eucaristia = random.choice(sim_nao)
    batismo = random.choice(sim_nao)
    status_crismando = random.choice(status)
    id_catequista = random.choice(ids_catequista)
    
    dados.append([nome, nome_mae, nome_pai, data_nascimento, endereco, cidade, telefone1, telefone2, 
                  eucaristia, batismo, status_crismando, id_catequista])

# Criar DataFrame
colunas = ["Nome", "Nome da Mãe", "Nome do Pai", "Data de Nascimento", "Endereço", "Cidade", 
           "Telefone 1", "Telefone 2", "Recebeu Eucaristia", "Recebeu Batismo", "Status", "ID Catequista"]
df = pd.DataFrame(dados, columns=colunas)

# Salvar em um arquivo Excel
caminho_arquivo = "extras_files/criacao_registros/crismandos.xlsx"
df.to_excel(caminho_arquivo, index=False)

caminho_arquivo
