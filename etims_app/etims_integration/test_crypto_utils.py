# Copyright (c) 2026, Aaron Vekaria and contributors
# For license information, please see license.txt

from frappe.tests.utils import FrappeTestCase

from etims_app.etims_integration.crypto_utils import decrypt_value, encrypt_value

# Test-only fake keys — never real KRA/eTIMS secrets.
FAKE_AES_KEY_HEX = "000102030405060708090a0b0c0d0e0f"
OTHER_AES_KEY_HEX = "0f0e0d0c0b0a09080706050403020100"


class TestCryptoUtils(FrappeTestCase):
	def test_encrypt_then_decrypt_round_trip(self):
		plaintext = "FAKEVALUE1234567890"
		ciphertext = encrypt_value(plaintext, FAKE_AES_KEY_HEX)

		self.assertNotEqual(ciphertext, plaintext)
		self.assertEqual(decrypt_value(ciphertext, FAKE_AES_KEY_HEX), plaintext)

	def test_decrypt_with_wrong_key_fails(self):
		ciphertext = encrypt_value("FAKEVALUE", FAKE_AES_KEY_HEX)

		with self.assertRaises(Exception):
			decrypt_value(ciphertext, OTHER_AES_KEY_HEX)

	def test_decrypt_invalid_base64_fails(self):
		with self.assertRaises(Exception):
			decrypt_value("not-valid-base64!!", FAKE_AES_KEY_HEX)
