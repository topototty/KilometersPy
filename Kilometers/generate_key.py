from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(f"Ваш сгенерированный ключ: {key.decode()}")

