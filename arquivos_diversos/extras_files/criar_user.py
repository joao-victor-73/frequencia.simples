from werkzeug.security import generate_password_hash

senha = "123456"
senha_hash = generate_password_hash(senha)

print(senha_hash)
