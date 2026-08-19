# Copyright (c) 2026, Aaron Vekaria and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from etims_app.etims_integration.crypto_utils import decrypt_value

DATA_KEY_FIELDS = ["sdc_id", "device_serial_number", "mrc_no"]
PASSWORD_KEY_FIELDS = ["cmc_key", "intrl_key", "sign_key"]


class ETIMSSettings(Document):
	def validate(self):
		self.normalize_key_fields()

	def normalize_key_fields(self):
		"""If key/device values were entered as AES/Base64-encrypted blobs,
		decrypt them in place so downstream code always sees plaintext."""
		if self.key_input_format != "Encrypted (AES/Base64)":
			return

		aes_key = self.get_password("aes_key", raise_exception=False)
		if not aes_key:
			frappe.throw(frappe._("AES Key is required to decrypt Encrypted key values."))

		for fieldname in DATA_KEY_FIELDS:
			value = self.get(fieldname)
			if value:
				self.set(fieldname, self._decrypt_field(fieldname, value, aes_key))

		for fieldname in PASSWORD_KEY_FIELDS:
			value = self.get_password(fieldname, raise_exception=False)
			if value:
				self.set(fieldname, self._decrypt_field(fieldname, value, aes_key))

		self.key_input_format = "Decrypted (Plaintext)"

	def _decrypt_field(self, fieldname, value, aes_key):
		try:
			return decrypt_value(value, aes_key)
		except Exception:
			frappe.throw(
				frappe._(
					"Could not decrypt '{0}' — check the AES Key and that the value is valid Base64 ciphertext."
				).format(self.meta.get_label(fieldname))
			)

	def get_active_base_url(self):
		"""Return whichever base URL is active for the configured environment."""
		return self.production_base_url if self.environment == "Production" else self.sandbox_base_url
