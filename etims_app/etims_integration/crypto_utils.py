# Copyright (c) 2026, Aaron Vekaria and contributors
# For license information, please see license.txt

from base64 import b64decode, b64encode

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# AES/ECB/PKCS5Padding with Base64-encoded ciphertext, matching the Java
# keystore scheme used to export these values.


def decrypt_value(ciphertext_b64, aes_key_hex):
	key = bytes.fromhex(aes_key_hex)
	ciphertext = b64decode(ciphertext_b64)

	decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
	padded = decryptor.update(ciphertext) + decryptor.finalize()

	unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
	plaintext = unpadder.update(padded) + unpadder.finalize()

	return plaintext.decode("utf-8")


def encrypt_value(plaintext, aes_key_hex):
	key = bytes.fromhex(aes_key_hex)

	padder = padding.PKCS7(algorithms.AES.block_size).padder()
	padded = padder.update(plaintext.encode("utf-8")) + padder.finalize()

	encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
	ciphertext = encryptor.update(padded) + encryptor.finalize()

	return b64encode(ciphertext).decode("ascii")
