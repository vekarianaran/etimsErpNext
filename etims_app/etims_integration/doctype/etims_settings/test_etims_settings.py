# Copyright (c) 2026, Aaron Vekaria and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from etims_app.etims_integration.crypto_utils import encrypt_value

# Test-only fake key — never a real KRA/eTIMS secret.
FAKE_AES_KEY_HEX = "000102030405060708090a0b0c0d0e0f"


class TestETIMSSettings(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_get_active_base_url_defaults_to_sandbox(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.environment = "Sandbox"
		settings.sandbox_base_url = "https://sandbox.etims.example/api"
		settings.production_base_url = "https://production.etims.example/api"

		self.assertEqual(settings.get_active_base_url(), settings.sandbox_base_url)

	def test_get_active_base_url_uses_production_when_set(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.environment = "Production"
		settings.sandbox_base_url = "https://sandbox.etims.example/api"
		settings.production_base_url = "https://production.etims.example/api"

		self.assertEqual(settings.get_active_base_url(), settings.production_base_url)

	def test_normalize_decrypts_encrypted_key_fields(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.key_input_format = "Encrypted (AES/Base64)"
		settings.aes_key = FAKE_AES_KEY_HEX
		settings.sdc_id = encrypt_value("FAKESDC0001", FAKE_AES_KEY_HEX)
		settings.cmc_key = encrypt_value("FAKECMCKEY", FAKE_AES_KEY_HEX)

		settings.normalize_key_fields()

		self.assertEqual(settings.sdc_id, "FAKESDC0001")
		self.assertEqual(settings.get_password("cmc_key", raise_exception=False), "FAKECMCKEY")
		self.assertEqual(settings.key_input_format, "Decrypted (Plaintext)")

	def test_normalize_leaves_plaintext_fields_untouched(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.key_input_format = "Decrypted (Plaintext)"
		settings.sdc_id = "PLAINSDC0001"

		settings.normalize_key_fields()

		self.assertEqual(settings.sdc_id, "PLAINSDC0001")

	def test_normalize_requires_aes_key_when_encrypted(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.key_input_format = "Encrypted (AES/Base64)"
		settings.aes_key = ""
		settings.sdc_id = encrypt_value("FAKESDC0001", FAKE_AES_KEY_HEX)

		self.assertRaises(frappe.ValidationError, settings.normalize_key_fields)

	def test_normalize_raises_clear_error_on_bad_ciphertext(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.key_input_format = "Encrypted (AES/Base64)"
		settings.aes_key = FAKE_AES_KEY_HEX
		settings.sdc_id = "not-valid-base64-ciphertext"

		self.assertRaises(frappe.ValidationError, settings.normalize_key_fields)
