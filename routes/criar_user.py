from werkzeug.security import generate_password_hash

senha = "sua_senha_aqui"
senha_hash = generate_password_hash(senha)

print(senha_hash)
