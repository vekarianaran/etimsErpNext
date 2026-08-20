# Copyright (c) 2026, Naran Vekaria and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from etims_app.etims_integration.crypto_utils import encrypt_value
from etims_app.etims_integration.doctype.etims_settings.etims_settings import PAIR_FIELDS

# Test-only fake key — never a real KRA/eTIMS secret.
FAKE_AES_KEY_HEX = "000102030405060708090a0b0c0d0e0f"


class TestETIMSSettings(FrappeTestCase):
	def setUp(self):
		self._reset_settings()

	def tearDown(self):
		self._reset_settings()
		frappe.db.rollback()

	def _reset_settings(self):
		settings = frappe.get_single("eTIMS Settings")
		for decrypted_field, encrypted_field in PAIR_FIELDS:
			settings.set(decrypted_field, "")
			settings.set(encrypted_field, "")
		settings.aes_key = ""
		settings.flags.ignore_validate = True
		settings.save()

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

	def test_decrypted_data_field_populates_encrypted_companion(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.aes_key = FAKE_AES_KEY_HEX
		settings.sdc_id = "FAKESDC0001"
		settings.save()

		self.assertEqual(settings.sdc_id_encrypted, encrypt_value("FAKESDC0001", FAKE_AES_KEY_HEX))

	def test_encrypted_data_field_populates_decrypted_companion(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.aes_key = FAKE_AES_KEY_HEX
		settings.sdc_id_encrypted = encrypt_value("FAKESDC0001", FAKE_AES_KEY_HEX)
		settings.save()

		self.assertEqual(settings.sdc_id, "FAKESDC0001")

	def test_decrypted_cmc_key_field_populates_encrypted_companion(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.aes_key = FAKE_AES_KEY_HEX
		settings.cmc_key = "FAKECMCKEY"
		settings.save()

		self.assertEqual(settings.cmc_key_encrypted, encrypt_value("FAKECMCKEY", FAKE_AES_KEY_HEX))

	def test_encrypted_cmc_key_field_populates_decrypted_companion(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.aes_key = FAKE_AES_KEY_HEX
		settings.cmc_key_encrypted = encrypt_value("FAKECMCKEY", FAKE_AES_KEY_HEX)
		settings.save()

		self.assertEqual(settings.cmc_key, "FAKECMCKEY")

	def test_conflicting_pair_edit_encrypted_wins(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.aes_key = FAKE_AES_KEY_HEX
		settings.sdc_id = "FAKESDC0001"
		settings.save()

		settings.sdc_id = "STALE-DECRYPTED-VALUE"
		settings.sdc_id_encrypted = encrypt_value("FRESH-FROM-KRA", FAKE_AES_KEY_HEX)
		settings.save()

		self.assertEqual(settings.sdc_id, "FRESH-FROM-KRA")

	def test_sync_requires_aes_key(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.aes_key = ""
		settings.sdc_id = "FAKESDC0001"

		self.assertRaises(frappe.ValidationError, settings.save)

	def test_sync_raises_clear_error_on_bad_ciphertext(self):
		settings = frappe.get_single("eTIMS Settings")
		settings.aes_key = FAKE_AES_KEY_HEX
		settings.sdc_id_encrypted = "not-valid-base64-ciphertext"

		self.assertRaises(frappe.ValidationError, settings.save)

	def test_removed_fields_are_gone(self):
		meta = frappe.get_meta("eTIMS Settings")
		fieldnames = {f.fieldname for f in meta.fields}

		for removed in ("device_mode", "key_input_format", "keystore_alias", "keystore_password"):
			self.assertNotIn(removed, fieldnames)

	def test_no_password_fieldtype_fields_remain(self):
		# Password fields route through Frappe's site-level encryption_key, which
		# is separate infrastructure from our own aes_key and was the cause of a
		# "Encryption key is in invalid format!" error unrelated to the AES Key
		# value itself. None of this doctype's fields should be Password anymore.
		meta = frappe.get_meta("eTIMS Settings")
		password_fields = [f.fieldname for f in meta.fields if f.fieldtype == "Password"]

		self.assertEqual(password_fields, [])
